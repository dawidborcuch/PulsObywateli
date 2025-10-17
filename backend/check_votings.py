#!/usr/bin/env python3
import requests
import json

def check_votings():
    """Sprawdź głosowania w API Sejmu"""
    try:
        # Pobierz listę głosowań
        votings_url = "https://api.sejm.gov.pl/sejm/term10/votings"
        response = requests.get(votings_url, timeout=30)
        response.raise_for_status()
        votings = response.json()
        
        print(f"Znaleziono {len(votings)} głosowań")
        
        # Sprawdź pierwsze 5 głosowań
        for i in range(min(5, len(votings))):
            voting = votings[i]
            proceeding_id = voting.get('proceeding', 1)
            voting_num = voting.get('votingsNum', 1)
            
            print(f"\n=== Głosowanie {i+1} ===")
            print(f"Posiedzenie: {proceeding_id}")
            print(f"Liczba głosowań: {voting_num}")
            print(f"Data: {voting.get('date')}")
            
            # Pobierz szczegóły pierwszego głosowania
            details_url = f"https://api.sejm.gov.pl/sejm/term10/votings/{proceeding_id}/1"
            details_response = requests.get(details_url, timeout=30)
            
            if details_response.status_code == 200:
                details = details_response.json()
                print(f"Temat: {details.get('topic', '')}")
                print(f"Opis: {details.get('description', '')}")
                print(f"Wyniki: Za={details.get('yes', 0)}, Przeciw={details.get('no', 0)}, Wstrzymali={details.get('abstain', 0)}")
                print(f"Liczba głosów posłów: {len(details.get('votes', []))}")
                
                # Sprawdź czy w temacie/opisie jest numer druku
                topic = details.get('topic', '').lower()
                description = details.get('description', '').lower()
                
                # Szukaj numerów druków w tekście
                import re
                druk_numbers = re.findall(r'druk\s*nr\s*(\d+)', topic + ' ' + description)
                if druk_numbers:
                    print(f"Znalezione numery druków: {druk_numbers}")
                else:
                    print("Brak numerów druków w temacie/opisie")
            else:
                print(f"Błąd pobierania szczegółów: {details_response.status_code}")
        
    except Exception as e:
        print(f"Błąd: {str(e)}")

if __name__ == "__main__":
    check_votings()
