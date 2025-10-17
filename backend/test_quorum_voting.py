#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.bills.views import get_voting_pdf_data
from django.test import RequestFactory

# Test głosowania kworum
factory = RequestFactory()
request = factory.get('/')
response = get_voting_pdf_data(request, 476)

print('Response status:', response.status_code)
print('Deputies count:', len(response.data.get('deputies', [])))

# Sprawdź statusy głosów
deputies = response.data.get('deputies', [])
vote_counts = {}
for deputy in deputies:
    vote = deputy['vote']
    vote_counts[vote] = vote_counts.get(vote, 0) + 1

print('Vote counts:', vote_counts)

# Pokaż przykłady
print('\nSample deputies:')
for i, deputy in enumerate(deputies[:10]):
    print(f'{i+1}. {deputy["first_name"]} {deputy["last_name"]} - {deputy["vote"]}')
