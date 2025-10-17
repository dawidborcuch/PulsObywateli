#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

def test_scraper():
    """Test scrapera strony Sejmu"""
    try:
        url = "https://www.sejm.gov.pl/sejm10.nsf/GlosowaniaLista.xsp"
        print(f"Pobieranie: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Sprawdź czy strona zawiera captcha
            if "What code is in the image" in response.text:
                print("❌ Strona wymaga captcha - nie można scrapować")
                return
            
            # Sprawdź czy są tabele
            tables = soup.find_all('table')
            print(f"Znaleziono {len(tables)} tabel")
            
            # Sprawdź czy są linki do posiedzeń
            links = soup.find_all('a', href=True)
            session_links = [link for link in links if 'GlosowaniaPosiedzenie' in link.get('href', '')]
            print(f"Znaleziono {len(session_links)} linków do posiedzeń")
            
            if session_links:
                print("Przykładowe linki:")
                for link in session_links[:3]:
                    print(f"  - {link.get('href')} - {link.get_text(strip=True)}")
            
            # Sprawdź czy są dane w tabelach
            for i, table in enumerate(tables):
                rows = table.find_all('tr')
                print(f"Tabela {i+1}: {len(rows)} wierszy")
                if rows:
                    # Sprawdź pierwszy wiersz
                    first_row = rows[0]
                    cells = first_row.find_all(['td', 'th'])
                    print(f"  Pierwszy wiersz: {len(cells)} komórek")
                    for j, cell in enumerate(cells[:5]):
                        print(f"    Komórka {j+1}: {cell.get_text(strip=True)[:50]}")
        else:
            print(f"Błąd HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"Błąd: {str(e)}")

if __name__ == "__main__":
    test_scraper()
