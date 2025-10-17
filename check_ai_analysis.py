#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bills.models import Bill

# Sprawdź głosowania z analizą AI
bills_with_ai = Bill.objects.filter(ai_analysis__isnull=False)
print(f"Głosowania z analizą AI: {bills_with_ai.count()}")

for bill in bills_with_ai:
    print(f"\nID: {bill.id}")
    print(f"Tytuł: {bill.title}")
    if bill.ai_analysis:
        print(f"Changes: {len(bill.ai_analysis.get('changes', ''))} znaków")
        print(f"Risks: {len(bill.ai_analysis.get('risks', ''))} znaków")
        print(f"Benefits: {len(bill.ai_analysis.get('benefits', ''))} znaków")
        print(f"Changes preview: {bill.ai_analysis.get('changes', '')[:200]}...")
    else:
        print("Brak analizy AI")
