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
        # Użyj pełnego tekstu jeśli dostępny, w przeciwnym razie użyj opisu
        if bill.full_text and len(bill.full_text) > 100:
            return bill.full_text[:8000]  # Ogranicz do 8000 znaków
        elif bill.description and len(bill.description) > 50:
            return bill.description
        else:
            return None
    
    def _create_analysis_prompt(self, text, title):
        """Tworzy prompt dla OpenAI"""
        return f"""
Przeanalizuj poniższy projekt ustawy i napisz analizę w języku polskim w następującym formacie:

**NAJWAŻNIEJSZE ZMIANY:**
[W kilku lub kilkunastu zdaniach opisz najważniejsze zmiany jakie wprowadza ten projekt]

**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**
[W kilku lub kilkunastu zdaniach opisz potencjalne zagrożenia jakie może nieść ten projekt]

**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**
[W kilku lub kilkunastu zdaniach opisz potencjalne korzyści jakie może przynieść ten projekt]

---

TYTUŁ PROJEKTU: {title}

TEKST DO ANALIZY:
{text}

---

Pamiętaj:
- Bądź obiektywny i rzeczowy
- Skup się na faktach, nie na opiniach politycznych
- Używaj języka zrozumiałego dla przeciętnego obywatela
- Jeśli nie ma wystarczających informacji, napisz o tym szczerze
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
            
            # Znajdź sekcje w tekście
            if '**NAJWAŻNIEJSZE ZMIANY:**' in response_text:
                changes_start = response_text.find('**NAJWAŻNIEJSZE ZMIANY:**') + len('**NAJWAŻNIEJSZE ZMIANY:**')
                changes_end = response_text.find('**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**', changes_start)
                if changes_end == -1:
                    changes_end = response_text.find('**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**', changes_start)
                if changes_end == -1:
                    changes_end = len(response_text)
                sections['changes'] = response_text[changes_start:changes_end].strip()
            
            if '**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**' in response_text:
                risks_start = response_text.find('**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**') + len('**ZAGROŻENIA DLA PAŃSTWA POLSKIEGO:**')
                risks_end = response_text.find('**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**', risks_start)
                if risks_end == -1:
                    risks_end = len(response_text)
                sections['risks'] = response_text[risks_start:risks_end].strip()
            
            if '**KORZYŚCI DLA PAŃSTWA POLSKIEGO:**' in response_text:
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
