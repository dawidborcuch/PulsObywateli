import requests
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bills.models import Bill
from datetime import datetime
import re


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

    def handle(self, *args, **options):
        limit = options['limit']
        term = options['term']
        force_update = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'Rozpoczynam pobieranie projektów ustaw z API Sejmu (kadencja {term})...')
        )
        
        try:
            bills_data = self.fetch_bills_from_sejm_api(term, limit)
            
            if not bills_data:
                self.stdout.write(self.style.WARNING('Nie znaleziono projektów ustaw w API Sejmu'))
                return
            
            created_count = 0
            updated_count = 0
            
            for bill_data in bills_data:
                bill, created = self.create_or_update_bill(bill_data, force_update)
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

    def fetch_bills_from_sejm_api(self, term, limit):
        """Pobiera dane projektów ustaw z API Sejmu"""
        bills_data = []
        
        try:
            # Pobierz listę projektów ustaw
            url = f"https://api.sejm.gov.pl/sejm/term{term}/processes"
            self.stdout.write(f'Pobieranie z: {url}')
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            processes = response.json()
            self.stdout.write(f'Znaleziono {len(processes)} procesów legislacyjnych')
            
            # Filtruj tylko projekty ustaw (nie uchwały)
            bill_processes = [p for p in processes if p.get('documentType') == 'ustawa']
            self.stdout.write(f'Znaleziono {len(bill_processes)} projektów ustaw')
            
            # Pobierz szczegóły dla każdego projektu
            for i, process in enumerate(bill_processes[:limit]):
                try:
                    bill_data = self.fetch_bill_details(term, process)
                    if bill_data:
                        bills_data.append(bill_data)
                        self.stdout.write(f'Pobrano projekt {i+1}/{min(limit, len(bill_processes))}: {bill_data["title"][:50]}...')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Błąd pobierania projektu {process.get("number", "unknown")}: {str(e)}'))
                    continue
                    
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Błąd połączenia z API Sejmu: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd podczas pobierania listy projektów: {str(e)}'))
            
        return bills_data

    def fetch_bill_details(self, term, process):
        """Pobiera szczegóły konkretnego projektu ustawy"""
        try:
            process_id = process.get('number')
            if not process_id:
                return None
                
            # Pobierz szczegóły procesu
            details_url = f"https://api.sejm.gov.pl/sejm/term{term}/processes/{process_id}"
            response = requests.get(details_url, timeout=30)
            response.raise_for_status()
            
            details = response.json()
            
            # Pobierz informacje o głosowaniach
            voting_info = self.get_voting_info(term, process_id)
            
            # Pobierz informacje o drukach
            prints_info = self.get_prints_info(term, process_id)
            
            return self.parse_bill_from_api_data(details, voting_info, prints_info)
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd pobierania szczegółów projektu {process_id}: {str(e)}'))
            return None

    def get_voting_info(self, term, process_id):
        """Pobiera informacje o głosowaniach dla projektu"""
        try:
            # Pobierz głosowania związane z procesem
            votings_url = f"https://api.sejm.gov.pl/sejm/term{term}/votings"
            response = requests.get(votings_url, timeout=30)
            response.raise_for_status()
            
            votings = response.json()
            
            # Filtruj głosowania związane z tym procesem
            process_votings = []
            for voting in votings:
                if process_id in voting.get('title', ''):
                    process_votings.append(voting)
            
            return process_votings
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd pobierania głosowań dla {process_id}: {str(e)}'))
            return []

    def get_prints_info(self, term, process_id):
        """Pobiera informacje o drukach dla projektu"""
        try:
            # Pobierz druki związane z procesem
            prints_url = f"https://api.sejm.gov.pl/sejm/term{term}/prints"
            response = requests.get(prints_url, timeout=30)
            response.raise_for_status()
            
            prints = response.json()
            
            # Filtruj druki związane z tym procesem
            process_prints = []
            for print_item in prints:
                if process_id in print_item.get('title', ''):
                    process_prints.append(print_item)
            
            return process_prints
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd pobierania druków dla {process_id}: {str(e)}'))
            return []

    def parse_bill_from_api_data(self, details, voting_info, prints_info):
        """Parsuje dane projektu ustawy z API Sejmu"""
        try:
            # Podstawowe informacje
            title = details.get('title', '')
            title_final = details.get('titleFinal', '')
            description = details.get('description', '')
            number = details.get('number', '')
            
            # Status i daty
            status = self.determine_status(details)
            submission_date = self.parse_date(details.get('processStartDate'))
            
            # Autorzy (z druków)
            authors = self.extract_authors(prints_info)
            
            # Linki
            source_url = details.get('address', '')
            if not source_url and details.get('links'):
                source_url = details.get('links')[0].get('href', '')
            
            # Tagi na podstawie tytułu
            tags = self.generate_tags_from_title(title)
            
            # Informacje o głosowaniach
            voting_summary = self.summarize_votings(voting_info)
            
            return {
                'number': number,
                'title': title_final if title_final else title,
                'description': f"{description}\n\n{voting_summary}",
                'authors': authors,
                'submission_date': submission_date,
                'status': status,
                'source_url': source_url,
                'tags': tags,
                'api_data': {
                    'sejm_id': details.get('number'),
                    'stages': details.get('stages', []),
                    'votings': voting_info,
                    'prints': prints_info,
                    'passed': details.get('passed', False),
                    'document_type': details.get('documentType', ''),
                    'eli': details.get('ELI', ''),
                }
            }
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd parsowania danych projektu: {str(e)}'))
            return None

    def determine_status(self, details):
        """Określa status projektu na podstawie etapów"""
        stages = details.get('stages', [])
        if not stages:
            return 'Nieznany'
        
        # Pobierz ostatni etap
        last_stage = stages[-1]
        stage_name = last_stage.get('stageName', '')
        
        # Mapowanie statusów
        status_mapping = {
            'Projekt wpłynął do Sejmu': 'Wpłynął do Sejmu',
            'Skierowano do I czytania na posiedzeniu Sejmu': 'I czytanie',
            'Skierowano do I czytania w komisjach': 'I czytanie w komisjach',
            'I czytanie na posiedzeniu Sejmu': 'I czytanie',
            'II czytanie na posiedzeniu Sejmu': 'II czytanie',
            'III czytanie na posiedzeniu Sejmu': 'III czytanie',
            'Ustawę przekazano Prezydentowi do podpisu': 'Przekazano Prezydentowi',
            'Ustawa została opublikowana': 'Opublikowana',
        }
        
        for key, value in status_mapping.items():
            if key in stage_name:
                return value
        
        return stage_name if stage_name else 'W trakcie'

    def parse_date(self, date_string):
        """Parsuje datę z API"""
        if not date_string:
            return timezone.now().date()
        
        try:
            # API zwraca daty w formacie ISO
            if 'T' in date_string:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
            else:
                return datetime.strptime(date_string, '%Y-%m-%d').date()
        except:
            return timezone.now().date()

    def extract_authors(self, prints_info):
        """Wyciąga autorów z druków"""
        authors = set()
        
        for print_item in prints_info:
            # Szukaj informacji o autorach w tytule lub opisie
            title = print_item.get('title', '')
            if 'rząd' in title.lower():
                authors.add('Rząd Rzeczypospolitej Polskiej')
            elif 'posłowie' in title.lower():
                authors.add('Grupa posłów')
            elif 'senat' in title.lower():
                authors.add('Senat RP')
        
        return ', '.join(authors) if authors else 'Nieznany'

    def generate_tags_from_title(self, title):
        """Generuje tagi na podstawie tytułu"""
        try:
            words = title.lower().split()
            stop_words = {'o', 'i', 'w', 'z', 'na', 'do', 'od', 'przy', 'dla', 'oraz', 'lub', 'ale', 'że', 'się', 'jest', 'są', 'być', 'mieć', 'ustawa', 'projekt'}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            tags = keywords[:5]
            tags_str = ', '.join(tags)
            
            if len(tags_str) > 200:
                tags_str = tags_str[:200]
                last_comma = tags_str.rfind(',')
                if last_comma > 0:
                    tags_str = tags_str[:last_comma]
            
            return tags_str
        except:
            return "ustawa, sejm, legislacja"

    def summarize_votings(self, voting_info):
        """Tworzy podsumowanie głosowań"""
        if not voting_info:
            return ""
        
        summary = f"\n\nGłosowania ({len(voting_info)}):\n"
        for voting in voting_info:
            title = voting.get('title', '')
            date = voting.get('date', '')
            summary += f"- {title} ({date})\n"
        
        return summary

    def create_or_update_bill(self, bill_data, force_update=False):
        """Tworzy lub aktualizuje projekt ustawy"""
        try:
            bill, created = Bill.objects.get_or_create(
                number=bill_data['number'],
                defaults={
                    'title': bill_data['title'],
                    'description': bill_data['description'],
                    'authors': bill_data['authors'],
                    'submission_date': bill_data['submission_date'],
                    'status': bill_data['status'],
                    'source_url': bill_data.get('source_url', ''),
                    'tags': bill_data.get('tags', ''),
                }
            )
            
            if not created and force_update:
                bill.title = bill_data['title']
                bill.description = bill_data['description']
                bill.authors = bill_data['authors']
                bill.submission_date = bill_data['submission_date']
                bill.status = bill_data['status']
                bill.source_url = bill_data.get('source_url', '')
                bill.tags = bill_data.get('tags', '')
                bill.save()
            
            return bill, created
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd tworzenia/aktualizacji projektu {bill_data["number"]}: {str(e)}'))
            return None, False
