import requests
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bills.models import Bill
from datetime import datetime
import re


class Command(BaseCommand):
    help = 'Pobiera projekty ustaw z API Sejmu RP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maksymalna liczba projektów do pobrania'
        )
        parser.add_argument(
            '--term',
            type=int,
            default=10,
            help='Numer kadencji Sejmu (domyślnie 10)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Wymuś aktualizację istniejących projektów'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        term = options['term']
        force_update = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'Rozpoczynam pobieranie projektów ustaw z API Sejmu...')
        )
        
        try:
            # Pobierz dane z API Sejmu
            sejm_bills = self.fetch_sejm_bills(term, limit)
            self.stdout.write(f'Pobrano {len(sejm_bills)} projektów z API Sejmu')
            
            # Zapisz do bazy
            created_count = 0
            updated_count = 0
            
            for bill_data in sejm_bills:
                bill, created = self.create_or_update_bill(bill_data, force_update)
                if created:
                    created_count += 1
                elif not created and force_update:
                    updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Pobieranie zakończone. Utworzono: {created_count}, Zaktualizowano: {updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd podczas pobierania danych: {str(e)}'))

    def fetch_sejm_bills(self, term, limit):
        """Pobiera dane projektów ustaw z API Sejmu używając endpointu /prints"""
        bills_data = []
        
        try:
            # Użyj endpointu /prints z sortowaniem według daty dostarczenia
            url = f"https://api.sejm.gov.pl/sejm/term{term}/prints"
            params = {
                'sort_by': '-deliveryDate',  # Sortuj malejąco według daty dostarczenia
                'limit': limit * 3  # Pobierz więcej, aby móc filtrować
            }
            self.stdout.write(f'Pobieranie z API Sejmu: {url}')
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            prints = response.json()
            self.stdout.write(f'Znaleziono {len(prints)} druków w API Sejmu')
            
            # Filtruj druki według daty (ostatnie 3 miesiące)
            filtered_prints = []
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=90)  # 3 miesiące temu
            
            # Debug: wyświetl daty druków
            self.stdout.write('=== DEBUG: DATY DRUKÓW ===')
            for i, print_item in enumerate(prints[:5]):
                delivery_date = print_item.get('deliveryDate', '')
                document_date = print_item.get('documentDate', '')
                self.stdout.write(f'{i+1}. Delivery: {delivery_date}, Document: {document_date}, Tytuł: {print_item.get("title", "")[:50]}...')
            
            for print_item in prints:
                try:
                    # Sprawdź datę dostarczenia lub datę dokumentu
                    delivery_date = print_item.get('deliveryDate', '')
                    document_date = print_item.get('documentDate', '')
                    
                    # Użyj daty dostarczenia, jeśli dostępna, w przeciwnym razie daty dokumentu
                    date_to_check = delivery_date if delivery_date else document_date
                    
                    if date_to_check:
                        try:
                            if 'T' in date_to_check:
                                date_obj = datetime.fromisoformat(date_to_check.replace('Z', '+00:00'))
                            else:
                                date_obj = datetime.strptime(date_to_check, '%Y-%m-%d')
                            
                            # Filtruj tylko druki z ostatnich 3 miesięcy
                            if date_obj >= cutoff_date:
                                filtered_prints.append(print_item)
                        except:
                            # Jeśli nie można sparsować daty, dodaj druk
                            filtered_prints.append(print_item)
                    else:
                        # Jeśli brak daty, dodaj druk
                        filtered_prints.append(print_item)
                except:
                    # Jeśli błąd, dodaj druk
                    filtered_prints.append(print_item)
            
            self.stdout.write(f'Po filtrowaniu daty: {len(filtered_prints)} druków z ostatnich 3 miesięcy')
            
            for i, print_item in enumerate(filtered_prints[:limit]):
                try:
                    bill_data = self.fetch_sejm_print_details(term, print_item)
                    if bill_data:
                        bills_data.append(bill_data)
                        self.stdout.write(f'Pobrano z API Sejmu {i+1}/{min(limit, len(filtered_prints))}: {bill_data["title"][:50]}...')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Błąd pobierania druku {print_item.get("number", "unknown")}: {str(e)}'))
                    continue
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd połączenia z API Sejmu: {str(e)}'))
            
        return bills_data

    def parse_pdf_content(self, pdf_content):
        """Parsuje zawartość PDF do tekstu"""
        try:
            import io
            import pdfplumber
            
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text.strip() if text.strip() else None
            
        except ImportError:
            self.stdout.write("pdfplumber nie jest zainstalowany. Instaluję...")
            import subprocess
            subprocess.check_call(["pip", "install", "pdfplumber"])
            return self.parse_pdf_content(pdf_content)
        except Exception as e:
            self.stdout.write(f'Błąd parsowania PDF: {str(e)}')
            return None

    def parse_docx_content(self, docx_content):
        """Parsuje zawartość DOCX do tekstu"""
        try:
            import io
            from docx import Document
            
            doc = Document(io.BytesIO(docx_content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip() if text.strip() else None
            
        except ImportError:
            self.stdout.write("python-docx nie jest zainstalowany. Instaluję...")
            import subprocess
            subprocess.check_call(["pip", "install", "python-docx"])
            return self.parse_docx_content(docx_content)
        except Exception as e:
            self.stdout.write(f'Błąd parsowania DOCX: {str(e)}')
            return None

    def extract_full_text_from_pdf_url(self, pdf_url, print_number):
        """Pobiera pełny tekst z PDF URL"""
        try:
            response = requests.get(pdf_url, timeout=30)
            if response.status_code == 200:
                # Tutaj można dodać parsowanie PDF (np. PyPDF2)
                self.stdout.write(f'Pobrano PDF z URL: {pdf_url} ({len(response.content)} bajtów)')
                # Na razie zwracamy informację o pobraniu
                return f"[PDF pobrany: {len(response.content)} bajtów]"
            else:
                self.stdout.write(f'Błąd pobierania PDF z URL {pdf_url}: HTTP {response.status_code}')
                return None
        except Exception as e:
            self.stdout.write(f'Błąd pobierania PDF z URL {pdf_url}: {str(e)}')
            return None

    def fetch_full_text_from_sejm_api(self, print_number):
        """Pobiera pełny tekst z API Sejmu"""
        try:
            # Spróbuj pobrać pełny tekst z endpointu /prints/{id}/text
            text_url = f"https://api.sejm.gov.pl/sejm/term10/prints/{print_number}/text"
            response = requests.get(text_url, timeout=30)
            
            if response.status_code == 200:
                return response.text
            else:
                self.stdout.write(f'Brak pełnego tekstu w API dla druku {print_number}')
                return None
                
        except Exception as e:
            self.stdout.write(f'Błąd pobierania pełnego tekstu z API: {str(e)}')
            return None

    def extract_full_text_from_attachments(self, term, print_number, attachments):
        """Pobiera pełny tekst z załączników używając API Sejmu"""
        try:
            full_text = ""
            attachment_files = []
            
            for attachment in attachments:
                if isinstance(attachment, dict):
                    # Nowa struktura API z title i url
                    title = attachment.get('title', '')
                    url = attachment.get('url', '')
                    file_name = title
                else:
                    # Stara struktura API (tylko nazwa pliku)
                    file_name = attachment
                
                # Określ typ pliku na podstawie nazwy
                file_type = 'unknown'
                if file_name.endswith('.pdf') or 'pdf' in file_name.lower():
                    file_type = 'pdf'
                elif file_name.endswith('.docx') or 'docx' in file_name.lower():
                    file_type = 'docx'
                elif file_name.endswith('.doc') or 'doc' in file_name.lower():
                    file_type = 'doc'
                
                # Użyj endpointu API Sejmu dla załączników
                api_url = f"https://api.sejm.gov.pl/sejm/term{term}/prints/{print_number}/{file_name}"
                
                try:
                    response = requests.get(api_url, timeout=30)
                    if response.status_code == 200:
                        # Sprawdź typ zawartości
                        content_type = response.headers.get('content-type', '').lower()
                        
                        if 'pdf' in content_type or file_type == 'pdf':
                            # Parsuj PDF
                            pdf_text = self.parse_pdf_content(response.content)
                            if pdf_text:
                                full_text += pdf_text + "\n\n"
                                attachment_files.append({
                                    'name': file_name,
                                    'type': file_type,
                                    'url': api_url,
                                    'size': len(response.content),
                                    'content': pdf_text[:500]  # Pierwsze 500 znaków jako podgląd
                                })
                                self.stdout.write(f'Pobrano i sparsowano PDF: {file_name} ({len(response.content)} bajtów, {len(pdf_text)} znaków tekstu)')
                            else:
                                self.stdout.write(f'Pobrano PDF: {file_name} ({len(response.content)} bajtów) - brak tekstu')
                                attachment_files.append({
                                    'name': file_name,
                                    'type': file_type,
                                    'url': api_url,
                                    'size': len(response.content),
                                    'content': ''
                                })
                        elif 'word' in content_type or file_type in ['docx', 'doc']:
                            # Parsuj DOCX
                            docx_text = self.parse_docx_content(response.content)
                            if docx_text:
                                full_text += docx_text + "\n\n"
                                attachment_files.append({
                                    'name': file_name,
                                    'type': file_type,
                                    'url': api_url,
                                    'size': len(response.content),
                                    'content': docx_text[:500]  # Pierwsze 500 znaków jako podgląd
                                })
                                self.stdout.write(f'Pobrano i sparsowano DOCX: {file_name} ({len(response.content)} bajtów, {len(docx_text)} znaków tekstu)')
                            else:
                                self.stdout.write(f'Pobrano DOCX: {file_name} ({len(response.content)} bajtów) - brak tekstu')
                                attachment_files.append({
                                    'name': file_name,
                                    'type': file_type,
                                    'url': api_url,
                                    'size': len(response.content),
                                    'content': ''
                                })
                        else:
                            self.stdout.write(f'Pobrano: {file_name} ({len(response.content)} bajtów) - nieznany typ zawartości: {content_type}')
                            attachment_files.append({
                                'name': file_name,
                                'type': file_type,
                                'url': api_url,
                                'size': len(response.content),
                                'content': ''
                            })
                    else:
                        self.stdout.write(f'Błąd pobierania {file_name} z API Sejmu: HTTP {response.status_code}')
                        # Dodaj załącznik z informacją o błędzie
                        attachment_files.append({
                            'name': file_name,
                            'type': file_type,
                            'url': api_url,
                            'size': 0,
                            'content': ''
                        })
                except Exception as e:
                    self.stdout.write(f'Błąd pobierania {file_name} z API Sejmu: {str(e)}')
                    # Dodaj załącznik z informacją o błędzie
                    attachment_files.append({
                        'name': file_name,
                        'type': file_type,
                        'url': api_url,
                        'size': 0,
                        'content': ''
                    })
            
            return full_text if full_text else None, attachment_files
            
        except Exception as e:
            self.stdout.write(f'Błąd przetwarzania załączników: {str(e)}')
            return None, []

    def fetch_sejm_print_details(self, term, print_item):
        """Pobiera szczegóły druku z API Sejmu"""
        try:
            print_number = print_item.get('number')
            if not print_number:
                return None
                
            # Pobierz szczegóły druku
            details_url = f"https://api.sejm.gov.pl/sejm/term{term}/prints/{print_number}"
            response = requests.get(details_url, timeout=30)
            response.raise_for_status()
            
            details = response.json()
            
            # Pobierz etapy z procesu jeśli dostępny
            process_prints = details.get('processPrint', [])
            if process_prints:
                try:
                    process_id = process_prints[0]
                    process_url = f"https://api.sejm.gov.pl/sejm/term{term}/processes/{process_id}"
                    process_response = requests.get(process_url, timeout=30)
                    if process_response.status_code == 200:
                        process_data = process_response.json()
                        details['stages'] = process_data.get('stages', [])
                        self.stdout.write(f'Pobrano {len(details["stages"])} etapów dla procesu {process_id}')
                except Exception as e:
                    self.stdout.write(f'Błąd pobierania etapów dla procesu {process_prints[0]}: {str(e)}')
                    details['stages'] = []
            
            # Określ typ projektu na podstawie tytułu
            title = details.get('title', '')
            project_type = self.determine_project_type(title)
            
            # Debug: wyświetl dostępne pola
            self.stdout.write(f'=== DEBUG: DOSTĘPNE POLA DLA DRUKU {print_number} ===')
            for key, value in details.items():
                if isinstance(value, str) and len(value) > 100:
                    self.stdout.write(f'{key}: {value[:100]}...')
                elif isinstance(value, list):
                    self.stdout.write(f'{key}: [lista z {len(value)} elementami]')
                    # Sprawdź szczegóły listy
                    if key == 'attachments' and value:
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                self.stdout.write(f'  - {i+1}: {item.get("title", "Brak tytułu")} - {item.get("url", "Brak URL")}')
                            else:
                                self.stdout.write(f'  - {i+1}: {item}')
                elif isinstance(value, dict):
                    self.stdout.write(f'{key}: [słownik z {len(value)} kluczami]')
                    # Sprawdź szczegóły słownika
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str) and len(sub_value) > 50:
                            self.stdout.write(f'  - {sub_key}: {sub_value[:50]}...')
                        else:
                            self.stdout.write(f'  - {sub_key}: {sub_value}')
                else:
                    self.stdout.write(f'{key}: {value}')
            
            # Sprawdź załączniki
            attachments = details.get('attachments', [])
            if attachments:
                self.stdout.write(f'=== ZAŁĄCZNIKI ({len(attachments)}): ===')
                for i, attachment in enumerate(attachments):
                    self.stdout.write(f'Załącznik {i+1}: {attachment}')
            
            # Sprawdź procesy
            process_prints = details.get('processPrint', [])
            if process_prints:
                self.stdout.write(f'=== PROCESY ({len(process_prints)}): ===')
                for i, process in enumerate(process_prints):
                    self.stdout.write(f'Proces {i+1}: {process}')
            
            # Pobierz pełny tekst z załączników
            full_text, attachment_files = self.extract_full_text_from_attachments(term, print_number, attachments)
            if full_text:
                self.stdout.write(f'=== PEŁNY TEKST Z ZAŁĄCZNIKÓW ({len(full_text)} znaków): ===')
                self.stdout.write(f'{full_text[:200]}...')
                self.stdout.write(f'=== ZAŁĄCZNIKI ({len(attachment_files)}): ===')
                for file in attachment_files:
                    self.stdout.write(f'- {file["name"]} ({file["type"]}, {file["size"]} bajtów)')
            else:
                self.stdout.write('=== BRAK PEŁNEGO TEKSTU W ZAŁĄCZNIKACH ===')
            
            return {
                'sejm_id': print_number,
                'title': title,
                'title_final': details.get('titleFinal', ''),
                'description': details.get('description', ''),
                'full_text': full_text,  # Pełny tekst z załączników
                'attachments': attachments,  # Lista załączników
                'attachment_files': attachment_files,  # Przechowywane pliki załączników
                'status': self.determine_sejm_status(details),
                'submission_date': self.parse_sejm_date(details.get('deliveryDate') or details.get('documentDate')),
                'authors': self.extract_sejm_authors(details),
                'source_url': details.get('address', ''),
                'stages': details.get('stages', []),
                'passed': details.get('passed', False),
                'document_type': details.get('documentType', ''),
                'eli': details.get('ELI', ''),
                'voting_data': self.extract_voting_data(details),
                'project_type': project_type,
                'api_data': details,  # Pełne dane z API
            }
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd pobierania szczegółów druku {print_number}: {str(e)}'))
            return None

    def fetch_sejm_bill_details(self, term, process):
        """Pobiera szczegóły projektu z API Sejmu"""
        try:
            process_id = process.get('number')
            if not process_id:
                return None
                
            details_url = f"https://api.sejm.gov.pl/sejm/term{term}/processes/{process_id}"
            response = requests.get(details_url, timeout=30)
            response.raise_for_status()
            
            details = response.json()
            
            # Określ typ projektu na podstawie tytułu
            title = details.get('title', '')
            project_type = self.determine_project_type(title)
            
            return {
                'sejm_id': process_id,
                'title': title,
                'title_final': details.get('titleFinal', ''),
                'description': details.get('description', ''),
                'status': self.determine_sejm_status(details),
                'submission_date': self.parse_sejm_date(details.get('processStartDate')),
                'authors': self.extract_sejm_authors(details),
                'source_url': details.get('address', ''),
                'stages': details.get('stages', []),
                'passed': details.get('passed', False),
                'document_type': details.get('documentType', ''),
                'eli': details.get('ELI', ''),
                'voting_data': self.extract_voting_data(details),
                'project_type': project_type,
                'api_data': details,  # Pełne dane z API
            }
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Błąd pobierania szczegółów projektu {process_id}: {str(e)}'))
            return None

    def extract_voting_data(self, details):
        """Wyciąga dane o głosowaniach z API Sejmu"""
        voting_data = []
        stages = details.get('stages', [])
        
        for stage in stages:
            if stage.get('stageType') == 'SejmReading' and stage.get('children'):
                for child in stage.get('children', []):
                    if child.get('stageType') == 'Voting' and child.get('voting'):
                        voting = child.get('voting', {})
                        voting_data.append({
                            'date': voting.get('date'),
                            'title': voting.get('title'),
                            'description': voting.get('description'),
                            'yes': voting.get('yes', 0),
                            'no': voting.get('no', 0),
                            'abstain': voting.get('abstain', 0),
                            'total_voted': voting.get('totalVoted', 0),
                            'majority_type': voting.get('majorityType'),
                            'majority_votes': voting.get('majorityVotes', 0),
                            'sitting': voting.get('sitting'),
                            'voting_number': voting.get('votingNumber'),
                            'links': voting.get('links', [])
                        })
        
        return voting_data





    def determine_sejm_status(self, details):
        """Określa status projektu na podstawie etapów z API Sejmu"""
        stages = details.get('stages', [])
        
        if not stages:
            # Fallback na podstawie tytułu
            title = details.get('title', '').lower()
            if 'sprawozdanie' in title:
                return 'Sprawozdanie'
            elif 'lista kandydatów' in title:
                return 'Nominacja'
            elif 'opinia' in title:
                return 'Opinia'
            else:
                return 'W trakcie'
        
        # Pobierz ostatni etap
        last_stage = stages[-1]
        stage_name = last_stage.get('stageName', '')
        
        # Mapowanie etapów z API na statusy
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
        
        return stage_mapping.get(stage_name, stage_name if stage_name else 'W trakcie')

    def parse_sejm_date(self, date_string):
        """Parsuje datę z API Sejmu"""
        if not date_string:
            return timezone.now().date()
        
        try:
            if 'T' in date_string:
                return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
            else:
                return datetime.strptime(date_string, '%Y-%m-%d').date()
        except:
            return timezone.now().date()

    def determine_project_type(self, title):
        """Określa typ projektu na podstawie tytułu"""
        if not title:
            return 'unknown'
        
        title_lower = title.lower()
        
        # Sprawdź kluczowe słowa w tytule
        if 'obywatelski projekt' in title_lower:
            return 'obywatelski'
        elif 'rządowy projekt' in title_lower:
            return 'rządowy'
        elif 'poselski projekt' in title_lower:
            return 'poselski'
        elif 'senacki projekt' in title_lower:
            return 'senacki'
        elif 'prezydencki projekt' in title_lower:
            return 'prezydencki'
        else:
            # Fallback - spróbuj wywnioskować z innych słów
            if 'obywatel' in title_lower:
                return 'obywatelski'
            elif 'rządowy' in title_lower or 'rząd' in title_lower:
                return 'rządowy'
            elif 'poseł' in title_lower or 'poselski' in title_lower:
                return 'poselski'
            elif 'senat' in title_lower or 'senacki' in title_lower:
                return 'senacki'
            elif 'prezydent' in title_lower or 'prezydencki' in title_lower:
                return 'prezydencki'
            else:
                return 'unknown'

    def extract_sejm_authors(self, details):
        """Wyciąga autorów z danych API Sejmu"""
        # Sprawdź w opisie
        description = details.get('description', '').lower()
        if 'rząd' in description:
            return 'Rząd Rzeczypospolitej Polskiej'
        elif 'posłowie' in description:
            return 'Grupa posłów'
        elif 'senat' in description:
            return 'Senat RP'
        
        return 'Nieznany'



    def generate_tags_from_title(self, title):
        """Generuje tagi na podstawie tytułu"""
        try:
            words = title.lower().split()
            stop_words = {'o', 'i', 'w', 'z', 'na', 'do', 'od', 'przy', 'dla', 'oraz', 'lub', 'ale', 'że', 'się', 'jest', 'są', 'być', 'mieć', 'ustawa', 'projekt'}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            tags = keywords[:3]  # Ogranicz do 3 tagów
            tags_str = ', '.join(tags)
            
            if len(tags_str) > 200:
                tags_str = tags_str[:200]
                last_comma = tags_str.rfind(',')
                if last_comma > 0:
                    tags_str = tags_str[:last_comma]
            
            return tags_str
        except:
            return "ustawa, sejm, legislacja"

    def create_or_update_bill(self, bill_data, force_update=False):
        """Tworzy lub aktualizuje projekt ustawy"""
        try:
            
            # Określ źródło danych i typ projektu
            data_source = 'sejm_api'
            project_type = bill_data.get('project_type', 'unknown')
            
            # Generuj numer projektu jeśli nie istnieje
            if not bill_data.get('number'):
                if bill_data.get('sejm_id'):
                    bill_data['number'] = f"SEJM/{bill_data['sejm_id']}"
                else:
                    # Fallback
                    bill_data['number'] = f"SEJM/{hash(bill_data.get('title', '')) % 10000}"
            
            bill, created = Bill.objects.get_or_create(
                number=bill_data['number'],
                defaults={
                    'title': bill_data['title'],
                    'description': bill_data['description'],
                    'authors': bill_data['authors'],
                    'submission_date': bill_data['submission_date'],
                    'status': bill_data['status'],
                    'source_url': bill_data.get('source_url', ''),
                    'tags': bill_data.get('tags', ''),
                    'data_source': data_source,
                    'project_type': project_type,
                    'api_data': bill_data.get('api_data', {}),
                    'sejm_id': bill_data.get('sejm_id', ''),
                    'eli': bill_data.get('eli', ''),
                    'document_type': bill_data.get('document_type', ''),
                    'passed': bill_data.get('passed', False),
                    'full_text': bill_data.get('full_text', ''),
                    'attachments': bill_data.get('attachments', []),
                    'attachment_files': bill_data.get('attachment_files', []),
                }
            )
            
            if not created and force_update:
                bill.title = bill_data['title']
                bill.description = bill_data['description']
                bill.authors = bill_data['authors']
                bill.submission_date = bill_data['submission_date']
                bill.status = bill_data['status']
                bill.source_url = bill_data.get('source_url', '')
                bill.tags = bill_data.get('tags', '')
                bill.data_source = data_source
                bill.project_type = project_type
                bill.api_data = bill_data.get('api_data', {})
                bill.sejm_id = bill_data.get('sejm_id', '')
                bill.eli = bill_data.get('eli', '')
                bill.document_type = bill_data.get('document_type', '')
                bill.passed = bill_data.get('passed', False)
                bill.full_text = bill_data.get('full_text', '')
                bill.attachments = bill_data.get('attachments', [])
                bill.attachment_files = bill_data.get('attachment_files', [])
                bill.save()
            
            return bill, created
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Błąd tworzenia/aktualizacji projektu {bill_data["number"]}: {str(e)}'))
            return None, False
