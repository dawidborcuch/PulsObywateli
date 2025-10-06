from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Poll(models.Model):
    """Model reprezentujący sondaż"""
    
    POLL_TYPES = [
        ('political', 'Polityczny'),
        ('social', 'Społeczny'),
        ('economic', 'Ekonomiczny'),
        ('other', 'Inny'),
    ]
    
    # Podstawowe informacje
    title = models.CharField(max_length=200, verbose_name="Tytuł sondażu")
    description = models.TextField(verbose_name="Opis")
    poll_type = models.CharField(max_length=20, choices=POLL_TYPES, default='political', verbose_name="Typ sondażu")
    
    # Opcje sondażu
    options = models.JSONField(verbose_name="Opcje sondażu", help_text="Lista opcji do wyboru")
    
    # Daty
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Data rozpoczęcia")
    end_date = models.DateTimeField(verbose_name="Data zakończenia")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Ustawienia
    is_active = models.BooleanField(default=True, verbose_name="Aktywny")
    is_featured = models.BooleanField(default=False, verbose_name="Wyróżniony")
    allow_multiple_votes = models.BooleanField(default=False, verbose_name="Pozwól na wielokrotne głosowanie")
    require_authentication = models.BooleanField(default=True, verbose_name="Wymagaj uwierzytelnienia")
    
    # Statystyki
    total_votes = models.PositiveIntegerField(default=0, verbose_name="Łączna liczba głosów")
    unique_voters = models.PositiveIntegerField(default=0, verbose_name="Unikalni głosujący")
    
    # Metadane
    tags = models.CharField(max_length=200, blank=True, verbose_name="Tagi", help_text="Tagi oddzielone przecinkami")
    
    class Meta:
        verbose_name = "Sondaż"
        verbose_name_plural = "Sondaże"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        """Czy sondaż jest w trakcie"""
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    @property
    def is_expired(self):
        """Czy sondaż wygasł"""
        return timezone.now() > self.end_date
    
    def get_tags_list(self):
        """Zwraca listę tagów"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_results(self):
        """Zwraca wyniki sondażu"""
        votes = self.votes.all()
        results = {}
        
        for option in self.options:
            option_votes = votes.filter(selected_option=option).count()
            percentage = (option_votes / self.total_votes * 100) if self.total_votes > 0 else 0
            results[option] = {
                'votes': option_votes,
                'percentage': round(percentage, 1)
            }
        
        return results
    
    def update_statistics(self):
        """Aktualizuje statystyki sondażu"""
        votes = self.votes.all()
        self.total_votes = votes.count()
        self.unique_voters = votes.values('user').distinct().count()
        self.save(update_fields=['total_votes', 'unique_voters'])


class PollVote(models.Model):
    """Model reprezentujący głos w sondażu"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes', null=True, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    selected_option = models.CharField(max_length=100, verbose_name="Wybrana opcja")
    
    # Informacje o głosującym (dla anonimowych głosów)
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adres IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    fingerprint = models.CharField(max_length=100, blank=True, verbose_name="Fingerprint przeglądarki")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Głos w sondażu"
        verbose_name_plural = "Głosy w sondażach"
        unique_together = ['user', 'poll']  # Jeden głos na użytkownika
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = self.user.nickname if self.user else f"Anonimowy ({self.ip_address})"
        return f"{user_info} - {self.poll.title}: {self.selected_option}"
    
    def save(self, *args, **kwargs):
        """Aktualizuje statystyki po zapisaniu głosu"""
        super().save(*args, **kwargs)
        self.poll.update_statistics()
    
    def delete(self, *args, **kwargs):
        """Aktualizuje statystyki po usunięciu głosu"""
        super().delete(*args, **kwargs)
        self.poll.update_statistics()


class PollComment(models.Model):
    """Model reprezentujący komentarz do sondażu"""
    
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_comments')
    content = models.TextField(verbose_name="Treść komentarza")
    is_approved = models.BooleanField(default=True, verbose_name="Zatwierdzony")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Komentarz do sondażu"
        verbose_name_plural = "Komentarze do sondaży"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nickname} - {self.poll.title}: {self.content[:50]}..."

