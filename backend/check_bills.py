#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bills.models import Bill
import re

# Sprawdź głosowania
bills = Bill.objects.all()
print(f"Łącznie głosowań: {bills.count()}")

print("\nGłosowania z numerami druków:")
for bill in bills:
    druki = re.findall(r'\d{3,5}', bill.title)
    if druki:
        print(f"ID: {bill.id}, Tytuł: {bill.title[:80]}..., Druki: {druki}")

print("\nWszystkie głosowania:")
for bill in bills:
    print(f"ID: {bill.id}, Tytuł: {bill.title[:80]}...")
