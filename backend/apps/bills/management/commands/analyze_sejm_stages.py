"""
Management command do analizy etapów legislacyjnych z API Sejmu RP
"""
import requests
from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    help = 'Analizuje etapy legislacyjne z API Sejmu RP'

    def handle(self, *args, **options):
        self.stdout.write('Analizuję etapy legislacyjne z API Sejmu RP...')
        
        # Lista procesów do analizy
        processes = ['1796', '1793', '1791', '1779', '1778', '1777', '1776', '1775', '1774', '1773']
        all_stages = []
        all_stage_types = set()
        
        for proc in processes:
            try:
                response = requests.get(f'https://api.sejm.gov.pl/sejm/term10/processes/{proc}', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    stages = data.get('stages', [])
                    all_stages.extend(stages)
                    self.stdout.write(f'Proces {proc}: {len(stages)} etapów')
                    
                    # Zbierz typy etapów
                    for stage in stages:
                        stage_type = stage.get('stageType', '')
                        if stage_type:
                            all_stage_types.add(stage_type)
                else:
                    self.stdout.write(f'Błąd dla procesu {proc}: HTTP {response.status_code}')
            except Exception as e:
                self.stdout.write(f'Błąd dla procesu {proc}: {str(e)}')
        
        # Analiza unikalnych nazw etapów
        unique_stage_names = set()
        for stage in all_stages:
            stage_name = stage.get('stageName', '')
            if stage_name:
                unique_stage_names.add(stage_name)
        
        self.stdout.write('\n=== UNIKALNE NAZWY ETAPÓW ===')
        for stage_name in sorted(unique_stage_names):
            self.stdout.write(f'- {stage_name}')
        
        self.stdout.write('\n=== TYPY ETAPÓW ===')
        for stage_type in sorted(all_stage_types):
            self.stdout.write(f'- {stage_type}')
        
        self.stdout.write('\n=== PRZYKŁADOWE ETAPY ===')
        for i, stage in enumerate(all_stages[:10]):
            self.stdout.write(f'{i+1}. {stage.get("stageName", "Brak nazwy")} ({stage.get("stageType", "Brak typu")})')
        
        self.stdout.write(f'\nZnaleziono {len(unique_stage_names)} unikalnych nazw etapów i {len(all_stage_types)} typów etapów.')
