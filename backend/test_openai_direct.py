#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import openai

# Testuj klucz bezpośrednio
try:
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test"}],
        max_tokens=10
    )
    print("OpenAI API działa poprawnie!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print("Błąd OpenAI API:", str(e))
