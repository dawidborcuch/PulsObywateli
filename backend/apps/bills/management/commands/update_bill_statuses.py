"""
Management command do aktualizacji statusów projektów ustaw na podstawie analizy tytułów
"""
from django.core.management.base import BaseCommand
from apps.bills.models import Bill


class Command(BaseCommand):
    help = 'Aktualizuje statusy projektów ustaw na podstawie analizy tytułów'

    def handle(self, *args, **options):
        self.stdout.write('Rozpoczynam aktualizację statusów projektów ustaw...')
        
        updated_count = 0
        
        for bill in Bill.objects.all():
            old_status = bill.status
            new_status = self.determine_bill_status(bill.title, bill.api_data)
            
            if new_status != old_status:
                bill.status = new_status
                bill.save()
                updated_count += 1
                self.stdout.write(f'Zaktualizowano {bill.number}: {old_status} -> {new_status}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Aktualizacja zakończona. Zaktualizowano {updated_count} projektów.')
        )

    def determine_bill_status(self, title, api_data):
        """Określa status projektu na podstawie analizy tytułu"""
        title_lower = title.lower()
        
        # Sprawdź czy to sprawozdanie komisji
        if 'sprawozdanie' in title_lower:
            if 'uchwała senatu' in title_lower:
                return 'Senat'
            elif 'rządowy projekt' in title_lower or 'poselski projekt' in title_lower:
                return 'W komisji'
            else:
                return 'Sprawozdanie'
        
        # Sprawdź czy to uchwała Senatu
        if 'uchwała senatu' in title_lower:
            return 'Senat'
        
        # Sprawdź czy to projekt ustawy
        if 'projekt ustawy' in title_lower:
            # Sprawdź typ projektu
            if 'rządowy projekt' in title_lower:
                return 'I czytanie'
            elif 'poselski projekt' in title_lower:
                return 'I czytanie'
            elif 'prezydencki projekt' in title_lower:
                return 'I czytanie'
            else:
                return 'I czytanie'
        
        # Sprawdź czy to lista kandydatów
        if 'lista kandydatów' in title_lower:
            return 'Nominacja'
        
        # Sprawdź czy to opinia
        if 'opinia' in title_lower:
            return 'Opinia'
        
        # Sprawdź czy to sprawozdanie z realizacji
        if 'sprawozdanie' in title_lower and ('realizacji' in title_lower or 'wykonywania' in title_lower):
            return 'Sprawozdanie'
        
        # Sprawdź czy to projekt uchwały
        if 'projekt uchwały' in title_lower:
            return 'I czytanie'
        
        # Domyślny status dla projektów ustaw
        if 'ustawa' in title_lower or 'projekt' in title_lower:
            return 'I czytanie'
        
        # Jeśli nie można określić, zwróć ogólny status
        return 'W trakcie'
