"""
Management command do analizy etapów legislacyjnych dla konkretnych projektów
"""
import requests
from django.core.management.base import BaseCommand
from apps.bills.models import Bill
import json


class Command(BaseCommand):
    help = 'Analizuje etapy legislacyjne dla konkretnych projektów'

    def handle(self, *args, **options):
        self.stdout.write('Analizuję etapy legislacyjne dla konkretnych projektów...')
        
        bills = Bill.objects.all()[:10]
        all_stages = []
        
        for bill in bills:
            try:
                process_prints = bill.api_data.get('processPrint', [])
                if process_prints:
                    process_id = process_prints[0]
                    response = requests.get(f'https://api.sejm.gov.pl/sejm/term10/processes/{process_id}', timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        stages = data.get('stages', [])
                        all_stages.extend(stages)
                        
                        self.stdout.write(f'\n{bill.number}: {bill.title[:60]}...')
                        self.stdout.write(f'  Proces: {process_id}')
                        self.stdout.write(f'  Etapy: {len(stages)}')
                        
                        for i, stage in enumerate(stages):
                            stage_name = stage.get('stageName', 'Brak nazwy')
                            stage_type = stage.get('stageType', 'Brak typu')
                            stage_date = stage.get('date', 'Brak daty')
                            self.stdout.write(f'    {i+1}. {stage_name} ({stage_type}) - {stage_date}')
                    else:
                        self.stdout.write(f'{bill.number}: Błąd HTTP {response.status_code}')
                else:
                    self.stdout.write(f'{bill.number}: Brak processPrint')
            except Exception as e:
                self.stdout.write(f'{bill.number}: Błąd - {str(e)}')
        
        # Analiza unikalnych etapów
        unique_stages = set()
        for stage in all_stages:
            stage_name = stage.get('stageName', '')
            if stage_name:
                unique_stages.add(stage_name)
        
        self.stdout.write('\n=== UNIKALNE ETAPY Z API ===')
        for stage in sorted(unique_stages):
            self.stdout.write(f'- {stage}')
        
        self.stdout.write(f'\nZnaleziono {len(unique_stages)} unikalnych etapów.')
