#!/usr/bin/env python3
import requests
import json
import re

def find_real_bill_votings():
    """Znajdź prawdziwe głosowania nad projektami ustaw"""
    try:
        # Pobierz listę głosowań
        votings_url = "https://api.sejm.gov.pl/sejm/term10/votings"
        response = requests.get(votings_url, timeout=30)
        response.raise_for_status()
        votings = response.json()
        
        print(f"Sprawdzam {len(votings)} głosowań...")
        
        bill_votings = []
        
        # Sprawdź głosowania z różnych posiedzeń (pomiń pierwsze, które to wybory)
        for i, voting in enumerate(votings[10:], 10):  # Zacznij od 10. głosowania
            proceeding_id = voting.get('proceeding', 1)
            voting_num = voting.get('votingsNum', 1)
            
            print(f"\nSprawdzam posiedzenie {proceeding_id} z {voting_num} głosowaniami...")
            
            # Sprawdź wszystkie głosowania w danym posiedzeniu
            for vote_num in range(1, min(voting_num + 1, 6)):  # Maksymalnie 5 głosowań na posiedzenie
                try:
                    details_url = f"https://api.sejm.gov.pl/sejm/term10/votings/{proceeding_id}/{vote_num}"
                    details_response = requests.get(details_url, timeout=30)
                    
                    if details_response.status_code == 200:
                        details = details_response.json()
                        topic = details.get('topic', '').lower()
                        description = details.get('description', '').lower()
                        title = details.get('title', '').lower()
                        
                        # Szukaj słów kluczowych związanych z ustawami
                        bill_keywords = ['ustawa', 'projekt ustawy', 'zmiana ustawy', 'druk nr', 'uchwalenie']
                        is_bill_voting = any(keyword in topic or keyword in description or keyword in title 
                                           for keyword in bill_keywords)
                        
                        if is_bill_voting:
                            # Szukaj numerów druków
                            text = topic + ' ' + description + ' ' + title
                            druk_numbers = re.findall(r'druk\s*nr\s*(\d+)', text)
                            
                            bill_votings.append({
                                'proceeding_id': proceeding_id,
                                'vote_num': vote_num,
                                'topic': details.get('topic', ''),
                                'description': details.get('description', ''),
                                'druk_numbers': druk_numbers,
                                'results': {
                                    'za': details.get('yes', 0),
                                    'przeciw': details.get('no', 0),
                                    'wstrzymali': details.get('abstain', 0)
                                },
                                'votes_count': len(details.get('votes', []))
                            })
                            
                            print(f"\n=== Znaleziono głosowanie nad projektem ustawy ===")
                            print(f"Posiedzenie: {proceeding_id}, Głosowanie: {vote_num}")
                            print(f"Temat: {details.get('topic', '')}")
                            print(f"Opis: {details.get('description', '')}")
                            print(f"Wyniki: Za={details.get('yes', 0)}, Przeciw={details.get('no', 0)}, Wstrzymali={details.get('abstain', 0)}")
                            print(f"Liczba głosów posłów: {len(details.get('votes', []))}")
                            if druk_numbers:
                                print(f"Numery druków: {druk_numbers}")
                            
                            # Ogranicz do pierwszych 5 znalezionych
                            if len(bill_votings) >= 5:
                                break
                
                except Exception as e:
                    continue
            
            if len(bill_votings) >= 5:
                break
        
        print(f"\n=== PODSUMOWANIE ===")
        print(f"Znaleziono {len(bill_votings)} głosowań nad projektami ustaw")
        
        # Wyświetl numery druków do pobrania
        all_druk_numbers = []
        for voting in bill_votings:
            all_druk_numbers.extend(voting['druk_numbers'])
        
        unique_druk_numbers = list(set(all_druk_numbers))
        print(f"Unikalne numery druków: {unique_druk_numbers}")
        
        # Jeśli nie ma numerów druków, spróbuj znaleźć inne projekty
        if not unique_druk_numbers:
            print("\n=== Szukam projektów ustaw w API /prints ===")
            prints_url = "https://api.sejm.gov.pl/sejm/term10/prints"
            prints_response = requests.get(prints_url, timeout=30)
            if prints_response.status_code == 200:
                prints = prints_response.json()
                print(f"Znaleziono {len(prints)} druków")
                
                # Szukaj projektów ustaw (nie sprawozdań)
                bill_prints = []
                for print_item in prints[:50]:  # Sprawdź pierwsze 50
                    title = print_item.get('title', '').lower()
                    if any(keyword in title for keyword in ['ustawa', 'projekt ustawy', 'zmiana ustawy']):
                        bill_prints.append(print_item)
                        print(f"Projekt ustawy: {print_item.get('number')} - {print_item.get('title', '')[:80]}...")
                        
                        if len(bill_prints) >= 5:
                            break
                
                return [p.get('number') for p in bill_prints]
        
        return unique_druk_numbers
        
    except Exception as e:
        print(f"Błąd: {str(e)}")
        return []

if __name__ == "__main__":
    find_real_bill_votings()
