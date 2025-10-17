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

# Sprawdź głosowania z drukami
bills = Bill.objects.all()
bills_with_prints = [bill for bill in bills if re.findall(r'\d{3,5}', bill.title)]

print(f"Głosowania z drukami: {len(bills_with_prints)}")

# Testuj AI dla pierwszego głosowania
if bills_with_prints:
    bill = bills_with_prints[0]
    print(f"\nTestuję AI dla głosowania ID: {bill.id}")
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
    else:
        print("OpenAI nie jest skonfigurowane!")
