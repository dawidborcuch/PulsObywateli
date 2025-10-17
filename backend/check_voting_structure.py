#!/usr/bin/env python3
import requests
import json

def check_voting_structure():
    """Sprawdź strukturę głosowań"""
    try:
        # Pobierz głosowania
        votings_url = "https://api.sejm.gov.pl/sejm/term10/votings"
        response = requests.get(votings_url, timeout=30)
        response.raise_for_status()
        votings = response.json()
        
        print(f"Znaleziono {len(votings)} głosowań")
        print("\nPierwsze 5 głosowań:")
        
        for i, voting in enumerate(votings[:5]):
            print(f"\n{i+1}. Posiedzenie: {voting.get('proceeding')}")
            print(f"   Głosowań: {voting.get('votingsNum')}")
            print(f"   Data: {voting.get('date')}")
            
            # Sprawdź szczegóły pierwszego głosowania
            proceeding_id = voting.get('proceeding', 1)
            details_url = f"https://api.sejm.gov.pl/sejm/term10/votings/{proceeding_id}/1"
            details_response = requests.get(details_url, timeout=30)
            
            if details_response.status_code == 200:
                details = details_response.json()
                print(f"   Temat: {details.get('topic', '')}")
                print(f"   Opis: {details.get('description', '')}")
                print(f"   Wyniki: Za={details.get('yes', 0)}, Przeciw={details.get('no', 0)}")
                
                # Sprawdź czy w opisie jest numer druku
                description = details.get('description', '')
                if 'druk nr' in description.lower():
                    print(f"   🎯 ZAWIERA NUMER DRUKU: {description}")
            else:
                print(f"   Błąd pobierania szczegółów: {details_response.status_code}")
        
    except Exception as e:
        print(f"Błąd: {str(e)}")

if __name__ == "__main__":
    check_voting_structure()
