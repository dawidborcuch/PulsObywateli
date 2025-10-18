"""
Cache'owanie OCR dla PDF-ów projektów ustaw
"""
import os
import hashlib
import json
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class OCRCache:
    """Klasa do zarządzania cache'em OCR"""
    
    def __init__(self):
        self.cache_dir = os.path.join(settings.BASE_DIR, 'ocr_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cache_key(self, print_number, page_number=None):
        """Generuje klucz cache dla danego druku i strony"""
        if page_number is not None:
            return f"druk_{print_number}_page_{page_number}.txt"
        else:
            return f"druk_{print_number}_full.txt"
    
    def get_cached_text(self, print_number, page_number=None):
        """Pobiera tekst z cache"""
        cache_key = self.get_cache_key(print_number, page_number)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Błąd odczytu cache {cache_key}: {e}")
                return None
        return None
    
    def save_to_cache(self, print_number, text, page_number=None):
        """Zapisuje tekst do cache"""
        cache_key = self.get_cache_key(print_number, page_number)
        cache_path = os.path.join(self.cache_dir, cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Zapisano do cache: {cache_key}")
        except Exception as e:
            logger.error(f"Błąd zapisu cache {cache_key}: {e}")
    
    def clear_cache(self, print_number=None):
        """Czyści cache - opcjonalnie dla konkretnego druku"""
        if print_number:
            # Usuń cache dla konkretnego druku
            pattern = f"druk_{print_number}_"
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(pattern):
                    os.remove(os.path.join(self.cache_dir, filename))
                    logger.info(f"Usunięto cache: {filename}")
        else:
            # Usuń cały cache
            for filename in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, filename))
                logger.info(f"Usunięto cache: {filename}")
    
    def get_cache_stats(self):
        """Zwraca statystyki cache"""
        files = os.listdir(self.cache_dir)
        total_files = len(files)
        total_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in files)
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }


class Command(BaseCommand):
    help = 'Zarządzanie cache OCR'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Wyczyść cache OCR'
        )
        parser.add_argument(
            '--clear-druk',
            type=int,
            help='Wyczyść cache dla konkretnego druku'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Pokaż statystyki cache'
        )
    
    def handle(self, *args, **options):
        cache = OCRCache()
        
        if options['clear']:
            cache.clear_cache()
            self.stdout.write(self.style.SUCCESS('Wyczyszczono cały cache OCR'))
        
        elif options['clear_druk']:
            cache.clear_cache(options['clear_druk'])
            self.stdout.write(self.style.SUCCESS(f'Wyczyszczono cache dla druku {options["clear_druk"]}'))
        
        elif options['stats']:
            stats = cache.get_cache_stats()
            self.stdout.write(f'Cache OCR - Pliki: {stats["total_files"]}, Rozmiar: {stats["total_size_mb"]} MB')
            self.stdout.write(f'Katalog: {stats["cache_dir"]}')
        
        else:
            self.stdout.write('Użyj --help aby zobaczyć dostępne opcje')
