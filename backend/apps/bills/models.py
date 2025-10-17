from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Bill(models.Model):
    """Model reprezentujący projekt ustawy"""
    
    STATUS_CHOICES = [
        ('draft', 'Projekt'),
        ('submitted', 'Złożony'),
        ('in_committee', 'W komisji'),
        ('first_reading', 'Pierwsze czytanie'),
        ('second_reading', 'Drugie czytanie'),
        ('third_reading', 'Trzecie czytanie'),
        ('passed', 'Przyjęty'),
        ('rejected', 'Odrzucony'),
        ('withdrawn', 'Wycofany'),
    ]
    
    # Podstawowe informacje
    title = models.CharField(max_length=500, verbose_name="Tytuł")
    description = models.TextField(verbose_name="Opis")
    number = models.CharField(max_length=50, unique=True, verbose_name="Numer projektu")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    
    # Autorzy i inicjatorzy
    authors = models.TextField(verbose_name="Autorzy", help_text="Lista autorów projektu")
    initiators = models.TextField(blank=True, verbose_name="Inicjatorzy", help_text="Lista inicjatorów")
    
    # Daty
    submission_date = models.DateField(verbose_name="Data złożenia")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Linki i źródła
    source_url = models.URLField(max_length=500, blank=True, verbose_name="Link do źródła")
    document_url = models.URLField(max_length=500, blank=True, verbose_name="Link do dokumentu")
    
    # Statystyki głosowania
    support_votes = models.PositiveIntegerField(default=0, verbose_name="Głosy za")
    against_votes = models.PositiveIntegerField(default=0, verbose_name="Głosy przeciw")
    neutral_votes = models.PositiveIntegerField(default=0, verbose_name="Głosy neutralne")
    total_votes = models.PositiveIntegerField(default=0, verbose_name="Łączna liczba głosów")
    
    # Metadane
    is_active = models.BooleanField(default=True, verbose_name="Aktywny")
    is_featured = models.BooleanField(default=False, verbose_name="Wyróżniony")
    tags = models.CharField(max_length=200, blank=True, verbose_name="Tagi", help_text="Tagi oddzielone przecinkami")
    
    # Pełny tekst i załączniki
    full_text = models.TextField(blank=True, null=True, verbose_name="Pełny tekst", help_text="Pełny tekst projektu z załączników")
    attachments = models.JSONField(blank=True, null=True, verbose_name="Załączniki", help_text="Lista załączników (PDF, DOCX)")
    attachment_files = models.JSONField(blank=True, null=True, verbose_name="Pliki załączników", help_text="Przechowywane pliki załączników")
    
    # Analiza AI
    ai_analysis = models.JSONField(blank=True, null=True, verbose_name="Analiza AI", help_text="Analiza projektu przez AI (zmiany, zagrożenia, korzyści)")
    ai_analysis_date = models.DateTimeField(blank=True, null=True, verbose_name="Data analizy AI", help_text="Kiedy została wykonana analiza AI")
    
    # Głosowania w Sejmie (nowe dane ze strony Sejmu)
    voting_date = models.CharField(max_length=50, blank=True, verbose_name="Data głosowania", help_text="Data głosowania w Sejmie")
    voting_time = models.CharField(max_length=20, blank=True, verbose_name="Godzina głosowania", help_text="Godzina głosowania")
    session_number = models.CharField(max_length=10, blank=True, verbose_name="Nr posiedzenia", help_text="Numer posiedzenia Sejmu")
    voting_number = models.IntegerField(blank=True, null=True, verbose_name="Nr głosowania", help_text="Numer głosowania")
    voting_topic = models.TextField(blank=True, verbose_name="Temat głosowania", help_text="Temat głosowania")
    voting_results = models.JSONField(blank=True, null=True, verbose_name="Wyniki głosowania", help_text="Wyniki ogólne głosowania")
    club_results = models.JSONField(blank=True, null=True, verbose_name="Wyniki klubów", help_text="Wyniki głosowania według klubów")
    druk_numbers = models.JSONField(blank=True, null=True, verbose_name="Numery druków", help_text="Numery druków związane z głosowaniem")
    
    # Dane z API Sejmu
    sejm_id = models.CharField(max_length=50, blank=True, verbose_name="ID w API Sejmu", help_text="Identyfikator w systemie Sejmu")
    eli = models.URLField(max_length=500, blank=True, verbose_name="ELI", help_text="European Legislation Identifier")
    document_type = models.CharField(max_length=50, blank=True, verbose_name="Typ dokumentu", help_text="Typ dokumentu z API Sejmu")
    passed = models.BooleanField(default=False, verbose_name="Uchwalona", help_text="Czy ustawa została uchwalona")
    
    # Dane hybrydowe
    data_source = models.CharField(
        max_length=20, 
        choices=[
            ('sejm_api', 'API Sejmu'),
            ('gov_pl', 'Gov.pl'),
            ('hybrid', 'Hybrydowe'),
        ],
        default='hybrid',
        verbose_name="Źródło danych"
    )
    project_type = models.CharField(
        max_length=20,
        choices=[
            ('rządowy', 'Rządowy'),
            ('obywatelski', 'Obywatelski'),
            ('poselski', 'Poselski'),
            ('senacki', 'Senacki'),
            ('unknown', 'Nieznany'),
        ],
        default='unknown',
        verbose_name="Typ projektu"
    )
    api_data = models.JSONField(blank=True, null=True, verbose_name="Dane API", help_text="Dodatkowe dane z API")
    
    class Meta:
        verbose_name = "Projekt ustawy"
        verbose_name_plural = "Projekty ustaw"
        ordering = ['-submission_date', '-created_at']
    
    def __str__(self):
        return f"{self.number}: {self.title[:100]}"
    
    @property
    def support_percentage(self):
        """Procent poparcia"""
        if self.total_votes == 0:
            return 0
        return round((self.support_votes / self.total_votes) * 100, 1)
    
    @property
    def against_percentage(self):
        """Procent sprzeciwu"""
        if self.total_votes == 0:
            return 0
        return round((self.against_votes / self.total_votes) * 100, 1)
    
    @property
    def neutral_percentage(self):
        """Procent neutralnych"""
        if self.total_votes == 0:
            return 0
        return round((self.neutral_votes / self.total_votes) * 100, 1)
    
    def get_tags_list(self):
        """Zwraca listę tagów"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def update_vote_statistics(self):
        """Aktualizuje statystyki głosowania"""
        votes = self.votes.all()
        self.support_votes = votes.filter(vote='support').count()
        self.against_votes = votes.filter(vote='against').count()
        self.neutral_votes = votes.filter(vote='neutral').count()
        self.total_votes = votes.count()
        self.save(update_fields=['support_votes', 'against_votes', 'neutral_votes', 'total_votes'])


class BillVote(models.Model):
    """Model reprezentujący głos użytkownika na projekt ustawy"""
    
    VOTE_CHOICES = [
        ('support', 'Popieram'),
        ('against', 'Nie popieram'),
        ('neutral', 'Neutralny'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bill_votes')
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='votes')
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Głos na projekt ustawy"
        verbose_name_plural = "Głosy na projekty ustaw"
        unique_together = ['user', 'bill']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nickname} - {self.bill.number}: {self.get_vote_display()}"
    
    def save(self, *args, **kwargs):
        """Aktualizuje statystyki po zapisaniu głosu"""
        super().save(*args, **kwargs)
        self.bill.update_vote_statistics()
    
    def delete(self, *args, **kwargs):
        """Aktualizuje statystyki po usunięciu głosu"""
        super().delete(*args, **kwargs)
        self.bill.update_vote_statistics()


class BillUpdate(models.Model):
    """Model reprezentujący aktualizację statusu projektu ustawy"""
    
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='updates')
    old_status = models.CharField(max_length=20, choices=Bill.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Bill.STATUS_CHOICES)
    description = models.TextField(blank=True, verbose_name="Opis zmiany")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Aktualizacja projektu ustawy"
        verbose_name_plural = "Aktualizacje projektów ustaw"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bill.number}: {self.old_status} → {self.new_status}"
