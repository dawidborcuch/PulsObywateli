#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print('API Key configured:', bool(settings.OPENAI_API_KEY))
if settings.OPENAI_API_KEY:
    print('API Key starts with:', settings.OPENAI_API_KEY[:20])
    print('API Key length:', len(settings.OPENAI_API_KEY))
else:
    print('No API key found')
