from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Rozszerzony model użytkownika"""
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, unique=True, help_text="Publiczny pseudonim")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statystyki użytkownika
    votes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nickname']
    
    class Meta:
        verbose_name = 'Użytkownik'
        verbose_name_plural = 'Użytkownicy'
    
    def __str__(self):
        return f"{self.nickname} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.nickname


class UserProfile(models.Model):
    """Dodatkowy profil użytkownika"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Preferencje
    email_notifications = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=False)
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Jasny'), ('dark', 'Ciemny'), ('auto', 'Automatyczny')],
        default='auto'
    )
    
    # Statystyki aktywności
    last_activity = models.DateTimeField(default=timezone.now)
    total_votes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profil użytkownika'
        verbose_name_plural = 'Profile użytkowników'
    
    def __str__(self):
        return f"Profil {self.user.nickname}"
    
    def update_activity(self):
        """Aktualizuje ostatnią aktywność użytkownika"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

