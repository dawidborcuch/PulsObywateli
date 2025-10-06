from django.contrib import admin
from .models import Poll, PollVote, PollComment


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """Panel administracyjny dla sondaży"""
    list_display = ('title', 'poll_type', 'start_date', 'end_date', 'total_votes', 'is_active', 'is_featured')
    list_filter = ('poll_type', 'is_active', 'is_featured', 'start_date', 'end_date', 'created_at')
    search_fields = ('title', 'description', 'tags')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_votes', 'unique_voters')
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('title', 'description', 'poll_type', 'options')
        }),
        ('Daty', {
            'fields': ('start_date', 'end_date')
        }),
        ('Ustawienia', {
            'fields': ('is_active', 'is_featured', 'allow_multiple_votes', 'require_authentication')
        }),
        ('Statystyki', {
            'fields': ('total_votes', 'unique_voters'),
            'classes': ('collapse',)
        }),
        ('Opcje', {
            'fields': ('tags',)
        }),
        ('Daty systemowe', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'activate_polls', 'deactivate_polls']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} sondaży zostało wyróżnionych')
    mark_as_featured.short_description = 'Wyróżnij wybrane sondaże'
    
    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} sondaży zostało odznaczonych')
    mark_as_not_featured.short_description = 'Odznacz wybrane sondaże'
    
    def activate_polls(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} sondaży zostało aktywowanych')
    activate_polls.short_description = 'Aktywuj wybrane sondaże'
    
    def deactivate_polls(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} sondaży zostało dezaktywowanych')
    deactivate_polls.short_description = 'Dezaktywuj wybrane sondaże'


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    """Panel administracyjny dla głosów w sondażach"""
    list_display = ('user', 'poll_title', 'selected_option', 'created_at')
    list_filter = ('created_at', 'poll__poll_type', 'poll__is_active')
    search_fields = ('user__email', 'user__nickname', 'poll__title', 'selected_option')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def poll_title(self, obj):
        return obj.poll.title
    poll_title.short_description = 'Sondaż'
    
    fieldsets = (
        ('Głos', {
            'fields': ('user', 'poll', 'selected_option')
        }),
        ('Informacje techniczne', {
            'fields': ('ip_address', 'user_agent', 'fingerprint'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('created_at',)
        }),
    )


@admin.register(PollComment)
class PollCommentAdmin(admin.ModelAdmin):
    """Panel administracyjny dla komentarzy w sondażach"""
    list_display = ('user', 'poll_title', 'content_short', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'poll__poll_type')
    search_fields = ('user__email', 'user__nickname', 'poll__title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def poll_title(self, obj):
        return obj.poll.title
    poll_title.short_description = 'Sondaż'
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Treść'
    
    fieldsets = (
        ('Komentarz', {
            'fields': ('user', 'poll', 'content', 'is_approved')
        }),
        ('Daty', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} komentarzy zostało zatwierdzonych')
    approve_comments.short_description = 'Zatwierdź wybrane komentarze'
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} komentarzy zostało odrzuconych')
    disapprove_comments.short_description = 'Odrzuć wybrane komentarze'

