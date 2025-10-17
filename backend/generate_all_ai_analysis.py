#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bills.models import Bill
from apps.bills.services import AIAnalysisService
import re

# Znajdź głosowania z prawdziwymi numerami druków
bills = Bill.objects.all()
bills_with_real_prints = []

for bill in bills:
    druki = re.findall(r'\d{3,5}', bill.title)
    # Filtruj tylko numery 3-5 cyfrowe (nie 2025)
    real_prints = [d for d in druki if len(d) >= 3 and d != '2025']
    if real_prints:
        bills_with_real_prints.append((bill, real_prints))

print(f"Znaleziono {len(bills_with_real_prints)} głosowań z prawdziwymi drukami")

service = AIAnalysisService()
print(f"OpenAI configured: {service.is_openai_configured()}")

if not service.is_openai_configured():
    print("OpenAI nie jest skonfigurowane!")
    sys.exit(1)

# Generuj analizę AI dla każdego głosowania
for i, (bill, prints) in enumerate(bills_with_real_prints):
    print(f"\n=== Głosowanie {i+1}/{len(bills_with_real_prints)} ===")
    print(f"ID: {bill.id}")
    print(f"Druki: {prints}")
    print(f"Tytuł: {bill.title}")
    
    # Sprawdź czy już ma analizę
    if bill.ai_analysis:
        print("Już ma analizę AI, pomijam...")
        continue
    
    print("Generuję analizę AI...")
    try:
        analysis = service.analyze_bill(bill)
        
        if analysis.get('error'):
            print(f"Błąd: {analysis['error']}")
        else:
            # Zapisz analizę do bazy
            bill.ai_analysis = {
                'changes': analysis.get('changes', ''),
                'risks': analysis.get('risks', ''),
                'benefits': analysis.get('benefits', '')
            }
            bill.save()
            print("Analiza AI zapisana!")
            print(f"Changes: {len(analysis.get('changes', ''))} znaków")
            print(f"Risks: {len(analysis.get('risks', ''))} znaków")
            print(f"Benefits: {len(analysis.get('benefits', ''))} znaków")
            
    except Exception as e:
        print(f"Błąd podczas generowania analizy: {str(e)}")

print("\n=== Podsumowanie ===")
bills_with_ai = Bill.objects.filter(ai_analysis__isnull=False)
print(f"Głosowania z analizą AI: {bills_with_ai.count()}")
print(f"Łącznie głosowań: {Bill.objects.count()}")
