"""
Management command do generowania analiz AI dla projektów ustaw
"""
from django.core.management.base import BaseCommand
from apps.bills.models import Bill
from apps.bills.services import AIAnalysisService


class Command(BaseCommand):
    help = 'Generuje analizy AI dla projektów ustaw'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bill-id',
            type=int,
            help='ID konkretnego projektu do analizy'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Maksymalna liczba projektów do analizy (domyślnie 5)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Wymuś ponowną analizę nawet jeśli już istnieje'
        )
        parser.add_argument(
            '--status',
            type=str,
            help='Analizuj tylko projekty o określonym statusie'
        )

    def handle(self, *args, **options):
        self.stdout.write('Rozpoczynam generowanie analiz AI...')
        
        # Inicjalizuj serwis AI
        try:
            ai_service = AIAnalysisService()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Błąd inicjalizacji serwisu AI: {str(e)}')
            )
            return
        
        # Pobierz projekty do analizy
        bills_query = Bill.objects.all()
        
        if options['bill_id']:
            bills_query = bills_query.filter(id=options['bill_id'])
        
        if options['status']:
            bills_query = bills_query.filter(status=options['status'])
        
        if not options['force']:
            # Pomiń projekty które już mają analizę
            bills_query = bills_query.filter(ai_analysis__isnull=True)
        
        bills = bills_query[:options['limit']]
        
        if not bills:
            self.stdout.write('Brak projektów do analizy.')
            return
        
        self.stdout.write(f'Znaleziono {len(bills)} projektów do analizy.')
        
        # Analizuj każdy projekt
        success_count = 0
        error_count = 0
        
        for bill in bills:
            self.stdout.write(f'\n=== Analizuję projekt {bill.number}: {bill.title[:50]}... ===')
            
            try:
                # Sprawdź czy projekt ma tekst do analizy
                if not bill.full_text and not bill.description:
                    self.stdout.write(
                        self.style.WARNING(f'Projekt {bill.number} nie ma tekstu do analizy - pomijam')
                    )
                    continue
                
                # Wygeneruj analizę
                analysis = ai_service.analyze_bill(bill)
                
                if 'error' in analysis:
                    self.stdout.write(
                        self.style.ERROR(f'Błąd analizy: {analysis["error"]}')
                    )
                    error_count += 1
                    continue
                
                # Zapisz analizę
                if ai_service.save_analysis_to_bill(bill, analysis):
                    self.stdout.write(
                        self.style.SUCCESS(f'Analiza zapisana dla projektu {bill.number}')
                    )
                    success_count += 1
                    
                    # Wyświetl podsumowanie analizy
                    self.stdout.write('--- Podsumowanie analizy ---')
                    if analysis.get('changes'):
                        self.stdout.write(f'Zmiany: {analysis["changes"][:100]}...')
                    if analysis.get('risks'):
                        self.stdout.write(f'Zagrożenia: {analysis["risks"][:100]}...')
                    if analysis.get('benefits'):
                        self.stdout.write(f'Korzyści: {analysis["benefits"][:100]}...')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Błąd zapisywania analizy dla projektu {bill.number}')
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Błąd podczas analizy projektu {bill.number}: {str(e)}')
                )
                error_count += 1
        
        # Podsumowanie
        self.stdout.write(f'\n=== PODSUMOWANIE ===')
        self.stdout.write(f'Pomyślnie przeanalizowano: {success_count} projektów')
        self.stdout.write(f'Błędy: {error_count} projektów')
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS('Analiza AI zakończona pomyślnie!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Nie udało się przeanalizować żadnego projektu.')
            )
