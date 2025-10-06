"""
Management command do pobierania projektów ustaw z Sejmu RP
"""
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime
import re
from apps.bills.models import Bill


class Command(BaseCommand):
    help = 'Pobiera projekty ustaw z Sejmu RP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maksymalna liczba projektów do pobrania'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Wymuś aktualizację istniejących projektów'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        force = options['force']
        
        self.stdout.write('Rozpoczynam pobieranie projektów ustaw z Sejmu RP...')
        
        try:
            bills_data = self.fetch_bills_from_sejm(limit)
            created_count = 0
            updated_count = 0
            
            for bill_data in bills_data:
                bill, created = self.create_or_update_bill(bill_data, force)
                if created:
                    created_count += 1
                    self.stdout.write(f'Utworzono: {bill.number} - {bill.title[:50]}...')
                elif force:
                    updated_count += 1
                    self.stdout.write(f'Zaktualizowano: {bill.number} - {bill.title[:50]}...')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Pobieranie zakończone. Utworzono: {created_count}, Zaktualizowano: {updated_count}'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Błąd podczas pobierania danych: {str(e)}')

    def fetch_bills_from_sejm(self, limit):
        """Pobiera dane projektów ustaw z gov.pl (KPRM)"""
        bills_data = []
        page = 1
        size = 10  # Liczba projektów na stronę
        
        while len(bills_data) < limit:
            url = f"https://www.gov.pl/web/premier/rok--2025?page={page}&size={size}"
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.WARNING(f'Błąd połączenia z gov.pl (strona {page}): {str(e)}')
                )
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Znajdź listę projektów ustaw na tej stronie
            bill_links = soup.find_all('a', href=re.compile(r'/web/premier/projekt-ustawy'))
            
            if not bill_links:
                # Brak więcej projektów na tej stronie
                self.stdout.write(f'Brak więcej projektów na stronie {page}')
                break
            
            for link in bill_links:
                if len(bills_data) >= limit:
                    break
                    
                try:
                    bill_data = self.parse_bill_from_link(link)
                    if bill_data:
                        bills_data.append(bill_data)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Błąd parsowania projektu: {str(e)}')
                    )
                    continue
            
            page += 1
            
            # Zabezpieczenie przed nieskończoną pętlą
            if page > 20:  # Maksymalnie 20 stron
                self.stdout.write(
                    self.style.WARNING('Osiągnięto limit stron (20)')
                )
                break
        
        return bills_data

    def parse_bill_from_link(self, link):
        """Parsuje projekt ustawy z linku"""
        try:
            # URL do szczegółów
            detail_url = link.get('href', '')
            if not detail_url.startswith('http'):
                detail_url = f"https://www.gov.pl{detail_url}"
            
            # Znajdź tytuł w elemencie z klasą "title"
            title_element = link.find('div', class_='title')
            if not title_element:
                return None
            
            title = title_element.get_text(strip=True)
            
            # Znajdź opis w elemencie z klasą "intro"
            intro_element = link.find('div', class_='intro')
            intro_text = intro_element.get_text(strip=True) if intro_element else ''
            
            # Wyciągnij daty z opisu
            submission_date, status = self.parse_dates_and_status(intro_text)
            
            # Wygeneruj numer projektu na podstawie tytułu
            number = self.generate_bill_number(title)
            
            # Wyciągnij autorów (w tym przypadku to rząd)
            authors = "Rząd Rzeczypospolitej Polskiej"
            
            return {
                'number': number,
                'title': title,
                'description': f"{title}\n\n{intro_text}",
                'authors': authors,
                'submission_date': submission_date,
                'status': status,
                'source_url': detail_url,
                'tags': self.generate_tags(title),
            }
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Błąd parsowania projektu: {str(e)}')
            )
            return None

    def parse_dates_and_status(self, intro_text):
        """Parsuje daty i status z tekstu opisu"""
        try:
            # Domyślne wartości
            submission_date = timezone.now().date()
            status = 'submitted'
            
            # Szukaj dat w różnych formatach
            date_patterns = [
                r'(\d{1,2}\s+\w+\s+\d{4})',  # "2 października 2025"
                r'(\d{1,2}\.\d{1,2}\.\d{4})',  # "02.10.2025"
                r'(\d{4}-\d{2}-\d{2})',  # "2025-10-02"
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, intro_text)
                if match:
                    date_str = match.group(1)
                    parsed_date = self.parse_date(date_str)
                    if parsed_date:
                        submission_date = parsed_date
                        break
            
            # Określ status na podstawie tekstu
            if 'przyjęty przez rząd' in intro_text.lower():
                status = 'submitted'
            elif 'skierowany do sejmu' in intro_text.lower():
                status = 'submitted'
            elif 'w komisji' in intro_text.lower():
                status = 'in_committee'
            elif 'pierwsze czytanie' in intro_text.lower():
                status = 'first_reading'
            elif 'drugie czytanie' in intro_text.lower():
                status = 'second_reading'
            elif 'trzecie czytanie' in intro_text.lower():
                status = 'third_reading'
            elif 'przyjęty' in intro_text.lower():
                status = 'passed'
            elif 'odrzucony' in intro_text.lower():
                status = 'rejected'
            
            return submission_date, status
            
        except Exception:
            return timezone.now().date(), 'submitted'

    def parse_date(self, date_string):
        """Parsuje datę z tekstu"""
        if not date_string:
            return timezone.now().date()
        
        try:
            # Mapowanie polskich nazw miesięcy
            month_names = {
                'stycznia': '01', 'lutego': '02', 'marca': '03', 'kwietnia': '04',
                'maja': '05', 'czerwca': '06', 'lipca': '07', 'sierpnia': '08',
                'września': '09', 'października': '10', 'listopada': '11', 'grudnia': '12'
            }
            
            # Próbuj różne formaty daty
            date_formats = [
                '%d.%m.%Y',
                '%d-%m-%Y',
                '%Y-%m-%d',
                '%d/%m/%Y',
            ]
            
            # Sprawdź format z polskimi nazwami miesięcy
            for month_name, month_num in month_names.items():
                if month_name in date_string.lower():
                    # Zamień polską nazwę miesiąca na numer
                    date_str_clean = re.sub(r'\s+', ' ', date_string.lower().strip())
                    parts = date_str_clean.split()
                    if len(parts) >= 3:
                        day = parts[0].zfill(2)
                        month = month_num
                        year = parts[2]
                        formatted_date = f"{day}.{month}.{year}"
                        return datetime.strptime(formatted_date, '%d.%m.%Y').date()
            
            # Próbuj standardowe formaty
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            return timezone.now().date()
            
        except Exception:
            return timezone.now().date()

    def generate_bill_number(self, title):
        """Generuje numer projektu na podstawie tytułu"""
        try:
            # Wyciągnij wszystkie słowa kluczowe z tytułu
            words = title.split()
            # Filtruj tylko słowa alfanumeryczne i dłuższe niż 3 znaki
            keywords = [word for word in words if word.isalpha() and len(word) > 3]
            
            # Weź pierwsze 3-5 słów kluczowych i utwórz identyfikator
            identifier_parts = []
            for word in keywords[:5]:
                identifier_parts.append(word[:3])
            
            identifier = ''.join(identifier_parts)[:12]  # Maksymalnie 12 znaków
            
            # Dodaj rok
            current_year = timezone.now().year
            return f"GOV/{current_year}/{identifier.upper()}"
            
        except Exception:
            import hashlib
            # Jeśli nie udało się wygenerować z tytułu, użyj hash
            hash_obj = hashlib.md5(title.encode())
            return f"GOV/{timezone.now().year}/{hash_obj.hexdigest()[:8].upper()}"

    def generate_tags(self, title):
        """Generuje tagi na podstawie tytułu"""
        try:
            # Wyciągnij kluczowe słowa z tytułu
            words = title.lower().split()
            # Filtruj słowa kluczowe (pomijaj spójniki, przyimki)
            stop_words = {'o', 'i', 'w', 'z', 'na', 'do', 'od', 'przy', 'dla', 'oraz', 'lub', 'ale', 'że', 'się', 'jest', 'są', 'być', 'mieć'}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Weź pierwsze 5 słów kluczowych
            tags = keywords[:5]
            
            # Ogranicz długość do 200 znaków
            tags_str = ', '.join(tags)
            if len(tags_str) > 200:
                # Skróć tagi do 200 znaków
                tags_str = tags_str[:200]
                # Znajdź ostatni przecinek i obetnij tam
                last_comma = tags_str.rfind(',')
                if last_comma > 0:
                    tags_str = tags_str[:last_comma]
            
            return tags_str
            
        except Exception:
            return "ustawa, rząd, legislacja"

    def map_status(self, status_text):
        """Mapuje status z Sejmu RP na status w aplikacji"""
        status_mapping = {
            'złożony': 'submitted',
            'w komisji': 'in_committee',
            'pierwsze czytanie': 'first_reading',
            'drugie czytanie': 'second_reading',
            'trzecie czytanie': 'third_reading',
            'przyjęty': 'passed',
            'odrzucony': 'rejected',
            'wycofany': 'withdrawn',
        }
        
        return status_mapping.get(status_text, 'submitted')

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
                # Aktualizuj istniejący projekt
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
            self.stdout.write(
                self.style.ERROR(f'Błąd tworzenia/aktualizacji projektu {bill_data["number"]}: {str(e)}')
            )
            return None, False

