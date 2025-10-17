import requests
import pdfplumber
import io
import re

def parse_deputies_from_text(text):
    """Parsuje dane posłów z tekstu PDF"""
    deputies = []
    current_party = None
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Sprawdź czy to nazwa partii (np. "PiS(188)", "Konfederacja_KP(3)", "niez.(4)")
        party_match = re.search(r'^([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż_.-]+)\([0-9]+\)', line)
        if party_match:
            current_party = party_match.group(1).strip()
            print(f"Znaleziono partię: {current_party}")
            continue
        
        # Sprawdź czy to linia z posłami (zawiera skróty głosów)
        if current_party and any(word in line.lower() for word in ['za', 'pr.', 'wstrzymał', 'ng.', 'nie']):
            words = line.split()
            i = 0
            while i < len(words):
                if i + 1 < len(words):
                    if (words[i].isupper() and words[i+1].isupper() and 
                        i + 2 < len(words)):
                        
                        last_name = words[i]
                        first_name = words[i+1]
                        vote_short = words[i+2].lower()
                        
                        if vote_short == 'za':
                            vote = 'ZA'
                        elif vote_short == 'pr.':
                            vote = 'PRZECIW'
                        elif vote_short == 'wstrzymał':
                            vote = 'WSTRZYMAŁ'
                        elif vote_short == 'ng.':
                            vote = 'NIE GŁOSOWAŁ'
                        elif vote_short == 'nie' and i + 3 < len(words) and words[i+3].lower() == 'głosował':
                            vote = 'NIE GŁOSOWAŁ'
                            i += 4
                            deputies.append({
                                'party': current_party,
                                'first_name': first_name,
                                'last_name': last_name,
                                'vote': vote
                            })
                            continue
                        else:
                            i += 1
                            continue
                        
                        deputies.append({
                            'party': current_party,
                            'first_name': first_name,
                            'last_name': last_name,
                            'vote': vote
                        })
                        i += 3
                    else:
                        i += 1
                else:
                    i += 1
    
    return deputies

# Pobierz PDF
response = requests.get('https://api.sejm.gov.pl/sejm/term10/votings/43/75/pdf')
pdf = pdfplumber.open(io.BytesIO(response.content))

print(f'PDF ma {len(pdf.pages)} stron\n')

all_deputies = []
for page_num, page in enumerate(pdf.pages):
    print(f'=== Strona {page_num + 1} ===')
    text = page.extract_text()
    if text:
        deputies = parse_deputies_from_text(text)
        print(f'Znaleziono {len(deputies)} posłów na stronie {page_num + 1}\n')
        all_deputies.extend(deputies)

print(f'\n=== PODSUMOWANIE ===')
print(f'Łącznie posłów: {len(all_deputies)}')

from collections import Counter
party_counts = Counter(d['party'] for d in all_deputies)
print('\nPartie i liczba posłów:')
for party, count in sorted(party_counts.items()):
    print(f'{party}: {count}')

