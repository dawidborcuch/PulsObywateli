#!/usr/bin/env python3
import os
import sys
import django

# Dodaj ścieżkę do Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bills.models import Bill
from apps.bills.management.commands.fetch_hybrid_bills import Command
import requests

def fetch_bills_with_votes():
    """Pobierz projekty ustaw z głosowaniami"""
    
    # Numery druków z głosowaniami
    druk_numbers = ['9', '161', '174']
    
    print(f"Pobieranie projektów ustaw z głosowaniami: {druk_numbers}")
    
    # Stwórz instancję komendy
    command = Command()
    
    for druk_number in druk_numbers:
        print(f"\n=== Pobieranie druku {druk_number} ===")
        
        try:
            # Pobierz szczegóły druku
            details_url = f"https://api.sejm.gov.pl/sejm/term10/prints/{druk_number}"
            response = requests.get(details_url, timeout=30)
            response.raise_for_status()
            details = response.json()
            
            print(f"Tytuł: {details.get('title', '')}")
            print(f"Data: {details.get('deliveryDate', '')}")
            
            # Pobierz dane o głosowaniach - użyj prostszej metody
            voting_data = get_voting_data_for_druk(druk_number)
            
            if voting_data:
                print(f"✅ Znaleziono głosowanie: {voting_data['topic']}")
                print(f"Wyniki: Za={voting_data['results']['za']}, Przeciw={voting_data['results']['przeciw']}")
                print(f"Liczba głosów posłów: {len(voting_data['poslowie'])}")
            else:
                print("❌ Brak danych o głosowaniu")
            
            # Przygotuj dane do zapisania
            bill_data = {
                'sejm_id': druk_number,
                'title': details.get('title', ''),
                'title_final': details.get('titleFinal', ''),
                'description': details.get('description', ''),
                'full_text': '',  # Na razie bez pełnego tekstu
                'attachments': details.get('attachments', []),
                'attachment_files': [],
                'status': command.determine_sejm_status(details),
                'submission_date': command.parse_sejm_date(details.get('deliveryDate') or details.get('documentDate')),
                'authors': command.extract_sejm_authors(details),
                'source_url': details.get('address', ''),
                'stages': details.get('stages', []),
                'passed': details.get('passed', False),
                'document_type': details.get('documentType', ''),
                'eli': details.get('ELI', ''),
                'voting_data': command.extract_voting_data(details),
                'sejm_votes': voting_data,  # Dane o głosowaniach posłów
                'project_type': command.determine_project_type(details.get('title', '')),
                'api_data': details,
                'number': f"SEJM/{druk_number}",
                'tags': command.generate_tags_from_title(details.get('title', ''))
            }
            
            # Zapisz do bazy
            bill, created = command.create_or_update_bill(bill_data, force_update=True)
            if created:
                print(f"✅ Utworzono projekt: {bill.title[:50]}...")
            else:
                print(f"✅ Zaktualizowano projekt: {bill.title[:50]}...")
                
        except Exception as e:
            print(f"❌ Błąd pobierania druku {druk_number}: {str(e)}")
    
    print(f"\n=== PODSUMOWANIE ===")
    bills_with_votes = Bill.objects.filter(sejm_votes__isnull=False)
    print(f"Projekty z głosowaniami: {bills_with_votes.count()}")
    
    for bill in bills_with_votes:
        print(f"- {bill.sejm_id}: {bill.title[:50]}...")
        if bill.sejm_votes:
            votes = bill.sejm_votes
            print(f"  Głosowanie: {votes.get('topic', '')}")
            print(f"  Wyniki: Za={votes.get('results', {}).get('za', 0)}, Przeciw={votes.get('results', {}).get('przeciw', 0)}")
            print(f"  Posłów: {len(votes.get('poslowie', []))}")

def get_voting_data_for_druk(druk_number):
    """Pobierz dane głosowania dla konkretnego druku"""
    try:
        # Pobierz głosowania
        votings_url = "https://api.sejm.gov.pl/sejm/term10/votings"
        response = requests.get(votings_url, timeout=30)
        response.raise_for_status()
        votings = response.json()
        
        # Znajdź głosowanie z tym drukiem
        for voting in votings:
            proceeding_id = voting.get('proceeding', 1)
            voting_num = voting.get('votingsNum', 1)
            
            # Sprawdź wszystkie głosowania w posiedzeniu
            for vote_num in range(1, min(voting_num + 1, 20)):
                try:
                    details_url = f"https://api.sejm.gov.pl/sejm/term10/votings/{proceeding_id}/{vote_num}"
                    details_response = requests.get(details_url, timeout=30)
                    
                    if details_response.status_code == 200:
                        details = details_response.json()
                        description = details.get('description', '').lower()
                        
                        # Sprawdź czy w opisie jest nasz druk
                        if f'druk nr {druk_number}' in description:
                            # Znaleziono głosowanie!
                            votes = details.get('votes', [])
                            
                            # Przetwórz głosy posłów
                            poslowie = []
                            for vote in votes:
                                vote_value = vote.get('listVotes', '')
                                if vote_value == 'YES':
                                    glos = 'Za'
                                elif vote_value == 'NO':
                                    glos = 'Przeciw'
                                elif vote_value == 'ABSTAIN':
                                    glos = 'Wstrzymał się'
                                else:
                                    glos = 'Nie głosował'
                                
                                poslowie.append({
                                    'imie': vote.get('firstName', ''),
                                    'nazwisko': vote.get('lastName', ''),
                                    'klub': vote.get('club', ''),
                                    'glos': glos
                                })
                            
                            return {
                                'druk': druk_number,
                                'voting_id': f"{proceeding_id}_{vote_num}",
                                'topic': details.get('topic', ''),
                                'title': details.get('title', ''),
                                'date': details.get('date', ''),
                                'sitting': details.get('sitting', 0),
                                'sitting_day': details.get('sittingDay', 0),
                                'results': {
                                    'za': details.get('yes', 0),
                                    'przeciw': details.get('no', 0),
                                    'wstrzymali': details.get('abstain', 0),
                                    'nieobecni': details.get('notParticipating', 0),
                                    'total': details.get('totalVoted', 0),
                                    'present': details.get('present', 0)
                                },
                                'poslowie': poslowie
                            }
                
                except Exception as e:
                    continue
        
        return None
        
    except Exception as e:
        print(f"Błąd pobierania głosowania dla druku {druk_number}: {str(e)}")
        return None

if __name__ == "__main__":
    fetch_bills_with_votes()
