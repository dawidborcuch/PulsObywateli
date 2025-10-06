from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Comment(models.Model):
    """Model reprezentujący komentarz do projektu ustawy"""
    
    # Relacje
    bill = models.ForeignKey('bills.Bill', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bill_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Treść
    content = models.TextField(verbose_name="Treść komentarza")
    
    # Status
    is_approved = models.BooleanField(default=True, verbose_name="Zatwierdzony")
    is_edited = models.BooleanField(default=False, verbose_name="Edytowany")
    
    # Statystyki
    likes_count = models.PositiveIntegerField(default=0, verbose_name="Liczba polubień")
    dislikes_count = models.PositiveIntegerField(default=0, verbose_name="Liczba niepolubień")
    replies_count = models.PositiveIntegerField(default=0, verbose_name="Liczba odpowiedzi")
    
    # Daty
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Komentarz"
        verbose_name_plural = "Komentarze"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.nickname} - {self.bill.number}: {self.content[:50]}..."
    
    def update_replies_count(self):
        """Aktualizuje liczbę odpowiedzi"""
        self.replies_count = self.replies.count()
        self.save(update_fields=['replies_count'])
    
    def update_likes_statistics(self):
        """Aktualizuje statystyki polubień"""
        self.likes_count = self.likes.filter(is_like=True).count()
        self.dislikes_count = self.likes.filter(is_like=False).count()
        self.save(update_fields=['likes_count', 'dislikes_count'])


class CommentLike(models.Model):
    """Model reprezentujący polubienie/niepolubienie komentarza"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(verbose_name="Polubienie (True) / Niepolubienie (False)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Polubienie komentarza"
        verbose_name_plural = "Polubienia komentarzy"
        unique_together = ['user', 'comment']
        ordering = ['-created_at']
    
    def __str__(self):
        action = "Polubił" if self.is_like else "Nie polubił"
        return f"{self.user.nickname} {action} komentarz {self.comment.id}"
    
    def save(self, *args, **kwargs):
        """Aktualizuje statystyki po zapisaniu polubienia"""
        super().save(*args, **kwargs)
        self.comment.update_likes_statistics()
    
    def delete(self, *args, **kwargs):
        """Aktualizuje statystyki po usunięciu polubienia"""
        super().delete(*args, **kwargs)
        self.comment.update_likes_statistics()


class CommentReport(models.Model):
    """Model reprezentujący zgłoszenie nieodpowiedniego komentarza"""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Nieodpowiednia treść'),
        ('harassment', 'Nękanie'),
        ('hate_speech', 'Mowa nienawiści'),
        ('false_information', 'Fałszywe informacje'),
        ('other', 'Inne'),
    ]
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS, verbose_name="Powód zgłoszenia")
    description = models.TextField(blank=True, verbose_name="Dodatkowy opis")
    is_resolved = models.BooleanField(default=False, verbose_name="Rozwiązane")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Zgłoszenie komentarza"
        verbose_name_plural = "Zgłoszenia komentarzy"
        unique_together = ['user', 'comment']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Zgłoszenie komentarza {self.comment.id} przez {self.user.nickname}: {self.get_reason_display()}"

