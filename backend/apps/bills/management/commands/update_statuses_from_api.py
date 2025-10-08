"""
Management command do aktualizacji statusów na podstawie etapów z API Sejmu
"""
import requests
from django.core.management.base import BaseCommand
from apps.bills.models import Bill


class Command(BaseCommand):
    help = 'Aktualizuje statusy projektów na podstawie etapów z API Sejmu'

    def handle(self, *args, **options):
        self.stdout.write('Aktualizuję statusy na podstawie etapów z API Sejmu...')
        
        updated_count = 0
        
        for bill in Bill.objects.all():
            try:
                # Pobierz etapy z API procesu
                process_prints = bill.api_data.get('processPrint', [])
                if process_prints:
                    process_id = process_prints[0]
                    response = requests.get(f'https://api.sejm.gov.pl/sejm/term10/processes/{process_id}', timeout=10)
                    
                    if response.status_code == 200:
                        process_data = response.json()
                        stages = process_data.get('stages', [])
                        
                        if stages:
                            # Określ status na podstawie ostatniego etapu
                            last_stage = stages[-1]
                            stage_name = last_stage.get('stageName', '')
                            
                            # Mapowanie etapów na statusy (max 20 znaków)
                            stage_mapping = {
                                'Projekt wpłynął do Sejmu': 'Wpłynął do Sejmu',
                                'Skierowano do I czytania na posiedzeniu Sejmu': 'Skierowano do I czytania',
                                'Skierowano do I czytania w komisjach': 'Skierowano do I czytania',
                                'I czytanie na posiedzeniu Sejmu': 'I czytanie',
                                'I czytanie w komisjach': 'I czytanie',
                                'Praca w komisjach po I czytaniu': 'Praca w komisjach',
                                'II czytanie na posiedzeniu Sejmu': 'II czytanie',
                                'Praca w komisjach po II czytaniu': 'Praca w komisjach',
                                'III czytanie na posiedzeniu Sejmu': 'III czytanie',
                                'Stanowisko Senatu': 'Senat',
                                'Praca w komisjach nad stanowiskiem Senatu': 'Praca w komisjach',
                                'Uchwalono': 'Uchwalono',
                            }
                            
                            # Skróć status jeśli jest za długi
                            new_status = stage_mapping.get(stage_name, stage_name if stage_name else 'W trakcie')
                            if len(new_status) > 20:
                                new_status = new_status[:20]
                            
                            if new_status != bill.status:
                                old_status = bill.status
                                bill.status = new_status
                                bill.save()
                                updated_count += 1
                                self.stdout.write(f'Zaktualizowano {bill.number}: {old_status} -> {new_status}')
                            else:
                                self.stdout.write(f'{bill.number}: Status już aktualny ({bill.status})')
                        else:
                            self.stdout.write(f'{bill.number}: Brak etapów w API')
                    else:
                        self.stdout.write(f'{bill.number}: Błąd API {response.status_code}')
                else:
                    self.stdout.write(f'{bill.number}: Brak processPrint')
            except Exception as e:
                self.stdout.write(f'{bill.number}: Błąd - {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Aktualizacja zakończona. Zaktualizowano {updated_count} projektów.')
        )
