#!/usr/bin/env python3
import requests
import json

def debug_voting_search():
    """Debug wyszukiwania głosowań dla konkretnych druków"""
    
    druk_numbers = ['161', '174', '188']
    
    for druk_number in druk_numbers:
        print(f"\n=== DEBUG dla druku {druk_number} ===")
        
        # Pobierz listę posiedzeń
        proceedings_url = "https://api.sejm.gov.pl/sejm/term10/proceedings"
        proceedings_response = requests.get(proceedings_url, timeout=30)
        
        if proceedings_response.status_code == 200:
            proceedings = proceedings_response.json()
            print(f"Znaleziono {len(proceedings)} posiedzeń")
            
            # Sprawdź każde posiedzenie
            for proceeding in proceedings[:5]:  # Sprawdź pierwsze 5 posiedzeń
                agenda = proceeding.get('agenda', '')
                if druk_number in agenda:
                    print(f"✅ Znaleziono druku {druk_number} w agendzie posiedzenia {proceeding.get('id', 'unknown')}")
                    print(f"Agenda fragment: {agenda[:200]}...")
                    
                    # Sprawdź głosowania dla tego posiedzenia
                    proceeding_id = proceeding.get('id', 1)
                    votings_url = f"https://api.sejm.gov.pl/sejm/term10/votings"
                    votings_response = requests.get(votings_url, timeout=30)
                    
                    if votings_response.status_code == 200:
                        votings = votings_response.json()
                        proceeding_votings = [v for v in votings if v.get('proceeding') == proceeding_id]
                        print(f"Głosowania dla posiedzenia {proceeding_id}: {len(proceeding_votings)}")
                        
                        # Sprawdź szczegóły głosowań
                        for voting in proceeding_votings[:3]:  # Sprawdź pierwsze 3 głosowania
                            voting_num = voting.get('votingsNum', 1)
                            details_url = f"https://api.sejm.gov.pl/sejm/term10/votings/{proceeding_id}/{voting_num}"
                            details_response = requests.get(details_url, timeout=30)
                            
                            if details_response.status_code == 200:
                                details = details_response.json()
                                topic = details.get('topic', '').lower()
                                description = details.get('description', '').lower()
                                
                                if druk_number in topic or druk_number in description:
                                    print(f"🎯 ZNALEZIONO GŁOSOWANIE!")
                                    print(f"Temat: {details.get('topic', '')}")
                                    print(f"Opis: {details.get('description', '')}")
                                    print(f"Wyniki: Za={details.get('yes', 0)}, Przeciw={details.get('no', 0)}")
                                    print(f"Liczba głosów: {len(details.get('votes', []))}")
                                    
                                    # Pokaż przykładowe głosy
                                    votes = details.get('votes', [])
                                    if votes:
                                        print("Przykładowe głosy posłów:")
                                        for vote in votes[:3]:
                                            print(f"  - {vote.get('firstName')} {vote.get('lastName')} ({vote.get('club')}) → {vote.get('listVotes')}")
                else:
                    print(f"❌ Druku {druk_number} nie ma w agendzie posiedzenia {proceeding.get('id', 'unknown')}")
        else:
            print(f"Błąd pobierania posiedzeń: {proceedings_response.status_code}")

if __name__ == "__main__":
    debug_voting_search()
