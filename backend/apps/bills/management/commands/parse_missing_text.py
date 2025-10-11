"""
Komenda do ponownego parsowania projektów bez pełnego tekstu
"""
from django.core.management.base import BaseCommand
from django.db import models
from apps.bills.models import Bill
import requests
import io
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract

class Command(BaseCommand):
    help = 'Ponownie parsuje projekty bez pełnego tekstu używając OCR'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maksymalna liczba projektów do przetworzenia'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Wymuś ponowne parsowanie nawet jeśli tekst już istnieje'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        force = options['force']
        
        # Znajdź projekty bez tekstu
        if force:
            bills = Bill.objects.all()[:limit]
        else:
            bills = Bill.objects.filter(
                models.Q(full_text__isnull=True) | models.Q(full_text__exact='')
            )[:limit]
        
        self.stdout.write(f'Znaleziono {bills.count()} projektów do przetworzenia')
        
        for bill in bills:
            self.stdout.write(f'\n=== Przetwarzanie {bill.number} ===')
            
            if not bill.attachments:
                self.stdout.write(f'Brak załączników dla {bill.number}')
                continue
            
            # Pobierz pierwszy PDF załącznik
            pdf_attachment = None
            for attachment in bill.attachments:
                if attachment.endswith('.pdf'):
                    pdf_attachment = attachment
                    break
            
            if not pdf_attachment:
                self.stdout.write(f'Brak PDF załączników dla {bill.number}')
                continue
            
            # Pobierz PDF z API
            api_url = f"https://api.sejm.gov.pl/sejm/term10/prints/{bill.sejm_id}/{pdf_attachment}"
            
            try:
                response = requests.get(api_url, timeout=60)
                if response.status_code != 200:
                    self.stdout.write(f'Błąd pobierania PDF dla {bill.number}: {response.status_code}')
                    continue
                
                # Spróbuj standardowego parsowania
                text = self.parse_pdf_standard(response.content)
                
                # Jeśli brak tekstu, spróbuj OCR
                if not text:
                    self.stdout.write(f'Brak tekstu w PDF, próba OCR...')
                    text = self.parse_pdf_ocr(response.content)
                
                if text:
                    bill.full_text = text
                    bill.save()
                    self.stdout.write(self.style.SUCCESS(f'Pomyślnie sparsowano {bill.number}: {len(text)} znaków'))
                else:
                    self.stdout.write(self.style.WARNING(f'Nie udało się sparsować {bill.number}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Błąd przetwarzania {bill.number}: {str(e)}'))
    
    def parse_pdf_standard(self, pdf_content):
        """Standardowe parsowanie PDF"""
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip() if text.strip() else None
        except Exception as e:
            self.stdout.write(f'Błąd standardowego parsowania: {str(e)}')
            return None
    
    def parse_pdf_ocr(self, pdf_content):
        """Parsowanie PDF używając OCR"""
        try:
            # Konwertuj PDF na obrazy (pierwsze 5 stron)
            images = convert_from_bytes(pdf_content, first_page=1, last_page=5)
            
            text = ""
            for i, image in enumerate(images):
                try:
                    page_text = pytesseract.image_to_string(image, lang='pol')
                    if page_text.strip():
                        text += page_text + "\n"
                        self.stdout.write(f'OCR strona {i+1}: {len(page_text)} znaków')
                except Exception as e:
                    self.stdout.write(f'Błąd OCR dla strony {i+1}: {str(e)}')
            
            return text.strip() if text.strip() else None
            
        except Exception as e:
            self.stdout.write(f'Błąd OCR: {str(e)}')
            return None
