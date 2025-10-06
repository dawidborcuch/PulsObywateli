"""
Management command do pobierania projektów ustaw z oficjalnego API Sejmu RP
"""
import requests
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime
from apps.bills.models import Bill


class Command(BaseCommand):
    help = 'Pobiera projekty ustaw z oficjalnego API Sejmu RP'

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
        
        self.stdout.write('Rozpoczynam pobieranie projektów ustaw z API Sejmu RP...')
        
        try:
            bills_data = self.fetch_bills_from_api(limit)
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

    def fetch_bills_from_api(self, limit):
        """Pobiera dane projektów ustaw z oficjalnego API Sejmu RP"""
        url = "https://api.sejm.gov.pl/projekty"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise CommandError(f'Błąd połączenia z API Sejmu RP: {str(e)}')
        
        data = response.json()
        bills_data = []
        
        # API zwraca listę projektów
        for item in data[:limit]:
            try:
                bill_data = self.parse_bill_from_api(item)
                if bill_data:
                    bills_data.append(bill_data)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Błąd parsowania projektu: {str(e)}')
                )
                continue
        
        return bills_data

    def parse_bill_from_api(self, item):
        """Parsuje projekt ustawy z API"""
        try:
            # Mapowanie pól z API na nasze modele
            bill_data = {
                'number': item.get('numer', f"U/{item.get('id', 'unknown')}"),
                'title': item.get('tytul', 'Brak tytułu'),
                'description': item.get('opis', ''),
                'authors': item.get('autorzy', 'Nieznany autor'),
                'submission_date': self.parse_date(item.get('data_wprowadzenia')),
                'status': self.map_status(item.get('status')),
                'source_url': item.get('url', ''),
            }
            
            return bill_data
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Błąd parsowania projektu: {str(e)}')
            )
            return None

    def parse_date(self, date_string):
        """Parsuje datę z API"""
        if not date_string:
            return timezone.now().date()
        
        try:
            # Próbuj różne formaty daty
            date_formats = [
                '%Y-%m-%d',
                '%d.%m.%Y',
                '%d-%m-%Y',
                '%Y-%m-%dT%H:%M:%S',
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            
            return timezone.now().date()
            
        except Exception:
            return timezone.now().date()

    def map_status(self, status):
        """Mapuje status z API na status w aplikacji"""
        if not status:
            return 'submitted'
        
        status_mapping = {
            'wprowadzony': 'submitted',
            'w komisji': 'in_committee',
            'pierwsze czytanie': 'first_reading',
            'drugie czytanie': 'second_reading',
            'trzecie czytanie': 'third_reading',
            'przyjęty': 'passed',
            'odrzucony': 'rejected',
            'wycofany': 'withdrawn',
        }
        
        return status_mapping.get(status.lower(), 'submitted')

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
                bill.save()
            
            return bill, created
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Błąd tworzenia/aktualizacji projektu {bill_data["number"]}: {str(e)}')
            )
            return None, False
