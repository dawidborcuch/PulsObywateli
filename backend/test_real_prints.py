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

# Sprawdź głosowania z prawdziwymi numerami druków
bills = Bill.objects.all()
bills_with_real_prints = []

for bill in bills:
    druki = re.findall(r'\d{3,5}', bill.title)
    # Filtruj tylko numery 3-5 cyfrowe (nie 2025)
    real_prints = [d for d in druki if len(d) >= 3 and d != '2025']
    if real_prints:
        bills_with_real_prints.append((bill, real_prints))

print(f"Głosowania z prawdziwymi drukami: {len(bills_with_real_prints)}")

for bill, prints in bills_with_real_prints:
    print(f"ID: {bill.id}, Druki: {prints}, Tytuł: {bill.title[:80]}...")

# Testuj AI dla pierwszego głosowania z prawdziwymi drukami
if bills_with_real_prints:
    bill, prints = bills_with_real_prints[0]
    print(f"\nTestuję AI dla głosowania ID: {bill.id}")
    print(f"Druki: {prints}")
    print(f"Tytuł: {bill.title}")
    
    service = AIAnalysisService()
    print(f"OpenAI configured: {service.is_openai_configured()}")
    
    if service.is_openai_configured():
        print("Generuję analizę AI...")
        analysis = service.analyze_bill(bill)
        print(f"Analiza zakończona. Błąd: {analysis.get('error', 'None')}")
        print(f"Changes length: {len(analysis.get('changes', ''))}")
        print(f"Risks length: {len(analysis.get('risks', ''))}")
        print(f"Benefits length: {len(analysis.get('benefits', ''))}")
        
        if analysis.get('changes'):
            print(f"\nChanges preview: {analysis['changes'][:200]}...")
        if analysis.get('risks'):
            print(f"\nRisks preview: {analysis['risks'][:200]}...")
        if analysis.get('benefits'):
            print(f"\nBenefits preview: {analysis['benefits'][:200]}...")
    else:
        print("OpenAI nie jest skonfigurowane!")
