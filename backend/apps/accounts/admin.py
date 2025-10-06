from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Panel administracyjny dla użytkowników"""
    list_display = ('email', 'nickname', 'first_name', 'last_name', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_verified', 'created_at')
    search_fields = ('email', 'nickname', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dane osobowe', {'fields': ('first_name', 'last_name', 'nickname', 'avatar', 'bio', 'birth_date')}),
        ('Uprawnienia', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Ważne daty', {'fields': ('last_login', 'date_joined', 'created_at')}),
        ('Statystyki', {'fields': ('votes_count', 'comments_count')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nickname', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'date_joined', 'last_login')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Panel administracyjny dla profili użytkowników"""
    list_display = ('user', 'email_notifications', 'newsletter', 'theme', 'last_activity', 'total_votes', 'total_comments')
    list_filter = ('email_notifications', 'newsletter', 'theme', 'last_activity')
    search_fields = ('user__email', 'user__nickname')
    readonly_fields = ('last_activity', 'total_votes', 'total_comments', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Użytkownik', {'fields': ('user',)}),
        ('Preferencje', {'fields': ('email_notifications', 'newsletter', 'theme')}),
        ('Statystyki', {'fields': ('last_activity', 'total_votes', 'total_comments')}),
        ('Daty', {'fields': ('created_at', 'updated_at')}),
    )

