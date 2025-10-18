"""
Serwisy do analizy projektów ustaw przez AI
"""
import openai
from django.conf import settings
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Serwis do analizy projektów ustaw przez OpenAI"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=60.0
        )
    
    def is_openai_configured(self):
        """Sprawdza czy OpenAI API jest skonfigurowane"""
        return bool(settings.OPENAI_API_KEY)
    
    def analyze_bill(self, bill):
        """
        Analizuje projekt ustawy i generuje opis zmian, zagrożeń i korzyści
        
        Args:
            bill: Instancja modelu Bill
            
        Returns:
            dict: Analiza zawierająca klucze: changes, risks, benefits
        """
        try:
            # Przygotuj tekst do analizy
            text_to_analyze = self._prepare_text_for_analysis(bill)
            
            if not text_to_analyze:
                return {
                    'error': 'Brak tekstu do analizy',
                    'changes': '',
                    'risks': '',
                    'benefits': ''
                }
            
            # Wygeneruj prompt
            prompt = self._create_analysis_prompt(text_to_analyze, bill.title)
            
            # Wywołaj OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Jesteś ekspertem prawnym i politycznym specjalizującym się w analizie projektów ustaw w Polsce. Analizujesz projekty ustaw pod kątem ich wpływu na państwo polskie."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parsuj odpowiedź
            analysis_text = response.choices[0].message.content
            parsed_analysis = self._parse_analysis_response(analysis_text)
            
            return parsed_analysis
            
        except Exception as e:
            logger.error(f"Błąd podczas analizy AI dla projektu {bill.number}: {str(e)}")
            return {
                'error': f'Błąd analizy: {str(e)}',
                'changes': '',
                'risks': '',
                'benefits': ''
            }
    
    def _prepare_text_for_analysis(self, bill):
        """Przygotowuje tekst do analizy"""
        # Najpierw spróbuj pobrać PDF-y projektów ustaw
        project_text = self._get_project_pdfs_text(bill)
        if project_text:
            return project_text
        
        # Jeśli nie ma PDF-ów projektów, użyj pełnego tekstu jeśli dostępny
        if bill.full_text and len(bill.full_text) > 100:
            return bill.full_text[:8000]  # Ogranicz do 8000 znaków
        elif bill.description and len(bill.description) > 50:
            return bill.description
        else:
            return None
    
    def _get_project_pdfs_text(self, bill):
        """Pobiera tekst z PDF-ów projektów ustaw dla danego głosowania"""
        try:
            import requests
            import pdfplumber
            import io
            
            # Pobierz dane głosowania z API Sejmu
            voting_data = bill.api_data
            if not voting_data:
                return None
            
            # Wyciągnij numery druków z tytułu
            title = voting_data.get('title', '')
            print_numbers = self._extract_print_numbers_from_title(title)
            
            if not print_numbers:
                return None
            
            # Pobierz tekst ze wszystkich dostępnych PDF-ów
            all_pdf_texts = []
            for print_number in print_numbers:
                logger.info(f"Próbuję pobrać tekst z druku {print_number}")
                pdf_text = self._download_print_pdf_text(print_number)
                if pdf_text:
                    logger.info(f"Pobrano tekst z druku {print_number}, długość: {len(pdf_text)}")
                    all_pdf_texts.append(f"=== DRUK NR {print_number} ===\n{pdf_text}")
                else:
                    logger.warning(f"Nie udało się pobrać tekstu z druku {print_number}")
            
            if all_pdf_texts:
                # Połącz wszystkie PDF-y w jeden tekst
                combined_text = '\n\n'.join(all_pdf_texts)
                logger.info(f"Połączono {len(all_pdf_texts)} PDF-ów, łączna długość: {len(combined_text)}")
                
                # Jeśli tekst jest za długi, obetnij proporcjonalnie z każdego druku
                if len(combined_text) > 6000:
                    max_length = 6000
                    # Oblicz proporcjonalny limit dla każdego druku
                    per_document_limit = max_length // len(all_pdf_texts)
                    
                    truncated_texts = []
                    for doc_text in all_pdf_texts:
                        # Znajdź nagłówek druku
                        if '=== DRUK NR' in doc_text:
                            header_end = doc_text.find('\n', doc_text.find('=== DRUK NR'))
                            header = doc_text[:header_end + 1]
                            content = doc_text[header_end + 1:]
                            truncated_content = content[:per_document_limit - len(header)]
                            truncated_texts.append(header + truncated_content)
                        else:
                            truncated_texts.append(doc_text[:per_document_limit])
                    
                    combined_text = '\n\n'.join(truncated_texts)
                
                return combined_text
            
            logger.warning("Nie udało się pobrać tekstu z żadnego PDF-a")
            return None
            
        except Exception as e:
            logger.error(f"Błąd pobierania PDF-ów projektów dla {bill.number}: {str(e)}")
            return None
    
    def _extract_print_numbers_from_title(self, title):
        """Wyciąga numery druków z tytułu głosowania"""
        import re
        # Znajdź wszystkie liczby 3-5 cyfrowe
        numbers = re.findall(r'\d{3,5}', title)
        return numbers
    
    def _download_print_pdf_text(self, print_number):
        """Pobiera tekst z PDF-a dla danego numeru druku"""
        try:
            import requests
            import pdfplumber
            import io
            
            headers = {"Accept": "application/json"}
            url = f"https://api.sejm.gov.pl/sejm/term10/prints/{print_number}"
            
            # Pobierz metadane druku
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Znajdź pierwszy dostępny PDF
            pdf_url = None
            
            # Sprawdź główne załączniki
            for att in data.get("attachments", []):
                if att.endswith(".pdf"):
                    pdf_url = f"https://api.sejm.gov.pl/sejm/term10/prints/{print_number}/{att}"
                    break
            
            # Jeśli nie ma w głównych, sprawdź dodatkowe druki
            if not pdf_url:
                for add in data.get("additionalPrints", []):
                    for att in add.get("attachments", []):
                        if att.endswith(".pdf"):
                            pdf_url = f"https://api.sejm.gov.pl/sejm/term10/prints/{print_number}/{att}"
                            break
                    if pdf_url:
                        break
            
            if not pdf_url:
                return None
            
            # Pobierz PDF i wyciągnij tekst
            pdf_response = requests.get(pdf_url, timeout=30)
            pdf_response.raise_for_status()
            
            with pdfplumber.open(io.BytesIO(pdf_response.content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    # Najpierw spróbuj wyciągnąć tekst bezpośrednio
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 50:
                        text_parts.append(page_text)
                    else:
                        # Jeśli nie ma tekstu, użyj OCR
                        logger.info(f"Używam OCR dla strony {len(text_parts) + 1}")
                        ocr_text = self._extract_text_with_ocr(print_number)
                        if ocr_text:
                            text_parts.append(ocr_text)
                
                return '\n'.join(text_parts)
                
        except Exception as e:
            logger.error(f"Błąd pobierania PDF dla druku {print_number}: {str(e)}")
            return None
    
    def _extract_text_with_ocr(self, print_number):
        """Wyciąga tekst z PDF-a używając OCR z cache'owaniem"""
        try:
            from .management.commands.ocr_cache import OCRCache
            import pytesseract
            from pdf2image import convert_from_bytes
            import requests
            
            # Sprawdź cache
            cache = OCRCache()
            cached_text = cache.get_cached_text(print_number)
            if cached_text:
                logger.info(f"Używam cache OCR dla druku {print_number}")
                return cached_text
            
            # Pobierz PDF URL
            headers = {"Accept": "application/json"}
            url = f"https://api.sejm.gov.pl/sejm/term10/prints/{print_number}"
            response = requests.get(url, headers=headers, timeout=30)
            data = response.json()
            
            pdf_url = None
            for att in data.get("attachments", []):
                if att.endswith(".pdf"):
                    pdf_url = f"https://api.sejm.gov.pl/sejm/term10/prints/{print_number}/{att}"
                    break
            
            if not pdf_url:
                return None
            
            # Pobierz PDF
            pdf_response = requests.get(pdf_url, timeout=30)
            pdf_bytes = pdf_response.content
            
            # Konwertuj PDF na obrazy
            images = convert_from_bytes(pdf_bytes, dpi=300)
            
            if not images:
                return None
            
            # Użyj OCR na wszystkich obrazach
            all_text = []
            for i, image in enumerate(images):
                # Sprawdź cache dla konkretnej strony
                page_cached = cache.get_cached_text(print_number, i)
                if page_cached:
                    logger.info(f"Używam cache OCR dla druku {print_number}, strona {i+1}")
                    all_text.append(page_cached)
                else:
                    logger.info(f"Używam OCR dla druku {print_number}, strona {i+1}")
                    text = pytesseract.image_to_string(image, lang='pol')
                    if text.strip():
                        all_text.append(text.strip())
                        # Zapisz do cache
                        cache.save_to_cache(print_number, text.strip(), i)
            
            full_text = '\n'.join(all_text) if all_text else None
            
            # Zapisz pełny tekst do cache
            if full_text:
                cache.save_to_cache(print_number, full_text)
            
            return full_text
            
        except Exception as e:
            logger.error(f"Błąd OCR dla druku {print_number}: {str(e)}")
            return None
    
    def _create_analysis_prompt(self, text, title):
        """Tworzy prompt dla OpenAI"""
        return f"""
Przeanalizuj poniższy projekt ustawy (lub projekty ustaw) i napisz szczegółową analizę w języku polskim w następującym formacie:

**O CZYM JEST TEN PROJEKT:**
[Napisz w kilkunastu/kilkudziesięciu zdaniach szczegółowe omówienie tego projektu ustawy. Wyjaśnij co dokładnie reguluje, jakie zmiany wprowadza, jakie są jego główne postanowienia i cele. Opisz mechanizmy działania i sposób funkcjonowania nowych przepisów. Jeśli analizujesz kilka druków, uwzględnij wszystkie z nich i wyjaśnij ich wzajemne powiązania.]

**DOBRE STRONY PROJEKTU:**
[Napisz w kilkunastu/kilkudziesięciu zdaniach o potencjalnych korzyściach tego projektu dla Państwa Polskiego i obywateli polskich. Skup się na pozytywnych aspektach, które mogą przynieść korzyści gospodarcze, społeczne, prawne lub inne dla Polski i jej mieszkańców. Jeśli analizujesz kilka druków, uwzględnij korzyści z całego pakietu ustaw.]

**ZAGROŻENIA Z PROJEKTU:**
[Napisz w kilkunastu/kilkudziesięciu zdaniach o potencjalnych zagrożeniach tego projektu dla Państwa Polskiego i obywateli polskich. Przeanalizuj ryzyka, które mogą wyniknąć z wprowadzenia tych przepisów, potencjalne negatywne skutki dla gospodarki, społeczeństwa, praw obywatelskich lub innych aspektów życia w Polsce. Jeśli analizujesz kilka druków, uwzględnij zagrożenia z całego pakietu ustaw.]

---

TYTUŁ PROJEKTU: {title}

TEKST PROJEKTU USTAWY DO ANALIZY:
{text}

---

WYMAGANIA ANALIZY:
- Bądź obiektywny, rzeczowy i szczegółowy
- Skup się na faktach prawnych i ekonomicznych, nie na opiniach politycznych
- Używaj języka zrozumiałego dla przeciętnego obywatela
- Każda sekcja powinna zawierać 15-30 zdań szczegółowej analizy
- Jeśli analizujesz kilka druków, uwzględnij wszystkie w swojej analizie
- Jeśli nie ma wystarczających informacji w tekście, napisz o tym szczerze
- Analizuj projekt z perspektywy dobra Państwa Polskiego i jego obywateli
- Uwzględnij aspekty prawne, ekonomiczne, społeczne i polityczne
- Jeśli dokumenty zawierają różne wersje tego samego projektu, wyjaśnij różnice
"""
    
    def _parse_analysis_response(self, response_text):
        """Parsuje odpowiedź z OpenAI i wyciąga sekcje"""
        try:
            # Podziel na sekcje
            sections = {
                'changes': '',
                'risks': '',
                'benefits': ''
            }
            
            # Znajdź sekcje w tekście - nowe nazwy sekcji
            if '**O CZYM JEST TEN PROJEKT:**' in response_text:
                changes_start = response_text.find('**O CZYM JEST TEN PROJEKT:**') + len('**O CZYM JEST TEN PROJEKT:**')
                changes_end = response_text.find('**DOBRE STRONY PROJEKTU:**', changes_start)
                if changes_end == -1:
                    changes_end = response_text.find('**ZAGROŻENIA Z PROJEKTU:**', changes_start)
                if changes_end == -1:
                    changes_end = len(response_text)
                sections['changes'] = response_text[changes_start:changes_end].strip()
            
            if '**ZAGROŻENIA Z PROJEKTU:**' in response_text:
                risks_start = response_text.find('**ZAGROŻENIA Z PROJEKTU:**') + len('**ZAGROŻENIA Z PROJEKTU:**')
                risks_end = response_text.find('**DOBRE STRONY PROJEKTU:**', risks_start)
                if risks_end == -1:
                    risks_end = len(response_text)
                sections['risks'] = response_text[risks_start:risks_end].strip()
            
            # Fallback dla starych nazw sekcji
            elif '**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**' in response_text:
                risks_start = response_text.find('**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**') + len('**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**')
                risks_end = response_text.find('**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**', risks_start)
                if risks_end == -1:
                    risks_end = len(response_text)
                sections['risks'] = response_text[risks_start:risks_end].strip()
            
            if '**DOBRE STRONY PROJEKTU:**' in response_text:
                benefits_start = response_text.find('**DOBRE STRONY PROJEKTU:**') + len('**DOBRE STRONY PROJEKTU:**')
                benefits_end = response_text.find('**ZAGROŻENIA Z PROJEKTU:**', benefits_start)
                if benefits_end == -1:
                    benefits_end = len(response_text)
                sections['benefits'] = response_text[benefits_start:benefits_end].strip()
            
            # Fallback dla starych nazw sekcji
            elif '**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**' in response_text:
                benefits_start = response_text.find('**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**') + len('**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**')
                sections['benefits'] = response_text[benefits_start:].strip()
            
            return sections
            
        except Exception as e:
            logger.error(f"Błąd parsowania odpowiedzi AI: {str(e)}")
            return {
                'error': f'Błąd parsowania: {str(e)}',
                'changes': '',
                'risks': '',
                'benefits': ''
            }
    
    def save_analysis_to_bill(self, bill, analysis):
        """Zapisuje analizę do modelu Bill"""
        try:
            bill.ai_analysis = analysis
            bill.ai_analysis_date = timezone.now()
            bill.save(update_fields=['ai_analysis', 'ai_analysis_date'])
            return True
        except Exception as e:
            logger.error(f"Błąd zapisywania analizy dla projektu {bill.number}: {str(e)}")
            return False
