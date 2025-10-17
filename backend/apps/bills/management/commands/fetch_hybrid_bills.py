import requests
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bills.models import Bill
from apps.bills.services import AIAnalysisService
from datetime import datetime
import re

# Import konfiguracji Sejmu
try:
    from sejm_config import SEJM_TERM, CURRENT_PROCEEDING
except ImportError:
    # Fallback jeśli plik nie istnieje
    SEJM_TERM = 10
    CURRENT_PROCEEDING = 43


class Command(BaseCommand):
    help = 'Pobiera projekty ustaw z API Sejmu RP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maksymalna liczba projektów do pobrania'
        )
        parser.add_argument(
            '--term',
            type=int,
            default=10,
            help='Numer kadencji Sejmu (domyślnie 10)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Wymuś aktualizację istniejących projektów'
        )
        parser.add_argument(
            '--ai-analysis',
            action='store_true',
            help='Automatycznie generuj analizę AI dla nowych projektów'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        term = options['term']
        force_update = options['force']
        ai_analysis_enabled = options['ai_analysis']
        
        # Inicjalizuj serwis AI jeśli włączony
        ai_service = None
        if ai_analysis_enabled:
            ai_service = AIAnalysisService()
            if not ai_service.is_openai_configured():
                self.stdout.write(self.style.WARNING('OpenAI API key nie jest skonfigurowany. Analiza AI zostanie pominięta.'))
                ai_service = None
        
        self.stdout.write(
            self.style.SUCCESS(f'Rozpoczynam pobieranie projektów ustaw z API Sejmu (kadencja {term})...')
        )
        
        try:
            # Pobierz dane z API Sejmu
            sejm_bills = self.fetch_sejm_bills(term, limit)
            self.stdout.write(f'Pobrano {len(sejm_bills)} projektów z API Sejmu')
            
            # Zapisz do bazy
            created_count = 0
            updated_count = 0
            
            for bill_data in sejm_bills:
                bill, created = self.create_or_update_bill(bill_data, force_update, ai_service)
                if created:
                    created_count += 1
                elif not created and force_update:
                    updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Pobieranie zakończone. Utworzono: {created_count}, Zaktualizowano: {updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd podczas pobierania danych: {str(e)}'))

    def fetch_sejm_bills(self, term, limit):
        """
        Pobiera dane głosowań z API Sejmu RP dla aktualnego posiedzenia
        API: https://api.sejm.gov.pl/sejm/term{term}/votings/{proceeding}
        """
        bills_data = []
        
        try:
            # Użyj numeru kadencji i posiedzenia z konfiguracji
            url = f"https://api.sejm.gov.pl/sejm/term{SEJM_TERM}/votings/{CURRENT_PROCEEDING}"
            
            self.stdout.write(f'Pobieranie głosowań z API Sejmu...')
            self.stdout.write(f'URL: {url}')
            
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            votings = response.json()
            
            if not votings:
                self.stdout.write(self.style.WARNING(f'Brak głosowań dla posiedzenia {CURRENT_PROCEEDING}'))
                return bills_data
            
            self.stdout.write(f'Znaleziono {len(votings)} głosowań')
            
            # Przetwórz każde głosowanie na projekt ustawy
            for i, voting in enumerate(votings[:limit]):
                try:
                    bill_data = self.process_voting_data(voting, SEJM_TERM, CURRENT_PROCEEDING)
                    if bill_data:
                        bills_data.append(bill_data)
                        self.stdout.write(
                            f'✓ Przetworzono głosowanie {i+1}/{min(limit, len(votings))}: '
                            f'{bill_data["title"][:60]}...'
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Błąd przetwarzania głosowania nr {voting.get("votingNumber", "?")}: {str(e)}'
                        )
                    )
                    continue
            
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Błąd połączenia z API Sejmu: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd pobierania danych: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        return bills_data

    def process_voting_data(self, voting, term, proceeding):
        """
        Przetwarza dane głosowania z API na format projektu ustawy
        
        Kluczowe pola z API:
        - date: data i godzina głosowania
        - links: linki do PDF
        - title: tytuł
        - topic: opis
        - totalVoted: ilu posłów głosowało
        - votingNumber: numer głosowania
        - yes, no, abstain, notParticipating: wyniki głosowania
        - majorityVotes, majorityType: informacje o większości
        """
        try:
            # Wyciągnij dane z głosowania
            voting_date = voting.get('date', '')  # Format: "2025-10-15T10:11:50"
            voting_number = voting.get('votingNumber', '')
            title = voting.get('title', 'Głosowanie bez tytułu')
            topic = voting.get('topic', '')
            
            # Wyniki głosowania
            total_voted = voting.get('totalVoted', 0)
            yes_votes = voting.get('yes', 0)
            no_votes = voting.get('no', 0)
            abstain_votes = voting.get('abstain', 0)
            not_participating = voting.get('notParticipating', 0)
            majority_votes = voting.get('majorityVotes', 0)
            majority_type = voting.get('majorityType', '')
            
            # Link do PDF
            pdf_link = None
            links = voting.get('links', [])
            for link in links:
                if link.get('rel') == 'pdf':
                    pdf_link = link.get('href', '')
                    break
            
            # Parsuj datę
            submission_date = None
            if voting_date:
                try:
                    # Format: "2025-10-15T10:11:50"
                    submission_date = datetime.fromisoformat(voting_date).date()
                except:
                    submission_date = timezone.now().date()
            else:
                submission_date = timezone.now().date()
            
            # Utwórz unikalny ID
            sejm_id = f"term{term}_proc{proceeding}_vote{voting_number}"
            
            # Przygotuj dane głosowania do zapisu w JSONField
            voting_results = {
                'total_voted': total_voted,
                'za': yes_votes,
                'przeciw': no_votes,
                'wstrzymali': abstain_votes,
                'nie_glosowalo': not_participating,
                'majority_votes': majority_votes,
                'majority_type': majority_type
            }
            
            # Przygotuj załączniki (PDF)
            attachments = []
            if pdf_link:
                attachments.append({
                    'type': 'pdf',
                    'url': pdf_link,
                    'name': f'Głosowanie {voting_number} - PDF'
                })
            
            return {
                'sejm_id': sejm_id,
                'title': title,
                'description': topic,
                'submission_date': submission_date,
                'status': 'Zakończone',
                'authors': f'Sejm RP - Posiedzenie {proceeding}',
                'project_type': 'sejm_voting',
                'source_url': f"https://www.sejm.gov.pl/sejm{term}.nsf/agent.xsp?symbol=glosowania&NrKadencji={term}&NrPosiedzenia={proceeding}&NrGlosowania={voting_number}",
                'number': f"Głosowanie nr {voting_number}",
                'tags': self.generate_tags_from_title(title),
                'voting_date': voting_date,
                'voting_number': str(voting_number),
                'session_number': str(proceeding),
                'voting_topic': topic,
                'voting_results': voting_results,
                'attachments': attachments if attachments else None,
                'api_data': voting  # Zapisz pełne dane z API dla przyszłych potrzeb
            }
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd przetwarzania danych głosowania: {str(e)}'))
            return None

    def create_or_update_bill(self, bill_data, force_update=False, ai_service=None):
        """Tworzy lub aktualizuje projekt ustawy w bazie danych"""
        sejm_id = bill_data.get('sejm_id', '')
        
        # Sprawdź czy projekt już istnieje
        if sejm_id:
            bill, created = Bill.objects.get_or_create(
                sejm_id=sejm_id,
                defaults=bill_data
            )
        else:
            # Jeśli nie ma sejm_id, utwórz nowy
            bill = Bill.objects.create(**bill_data)
            created = True
        
        if not created and force_update:
            # Aktualizuj istniejący projekt
            for key, value in bill_data.items():
                setattr(bill, key, value)
            bill.save()
        
        # Generuj analizę AI jeśli włączona i projekt nowy lub nie ma analizy
        if ai_service and (created or not bill.ai_analysis):
            if bill.full_text:
                self.stdout.write(f'Generuję analizę AI dla projektu: {bill.title[:50]}...')
                try:
                    analysis = ai_service.analyze_bill(bill.full_text, bill.title)
                    bill.ai_analysis = analysis
                    bill.ai_analysis_date = timezone.now()
                    bill.save()
                    self.stdout.write(self.style.SUCCESS('✓ Analiza AI wygenerowana'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Błąd generowania analizy AI: {str(e)}'))
        
        return bill, created

    def generate_tags_from_title(self, title):
        """Generuje tagi na podstawie tytułu projektu"""
        common_topics = {
            'zdrowia': 'Zdrowie',
            'oświat': 'Oświata',
            'podatk': 'Podatki',
            'bezpieczeńst': 'Bezpieczeństwo',
            'transport': 'Transport',
            'środowisk': 'Środowisko',
            'gospod': 'Gospodarka',
            'prac': 'Praca',
            'emeryt': 'Emerytury',
            'rent': 'Renty',
            'rodzin': 'Rodzina',
            'mieszka': 'Mieszkalnictwo',
            'energet': 'Energetyka',
            'cyfryz': 'Cyfryzacja',
            'samorzą': 'Samorząd',
        }
        
        tags = []
        title_lower = title.lower()
        
        for keyword, tag in common_topics.items():
            if keyword in title_lower:
                tags.append(tag)
        
        return tags[:3]  # Max 3 tagi
