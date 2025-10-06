from django.contrib import admin
from .models import Comment, CommentLike, CommentReport


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Panel administracyjny dla komentarzy"""
    list_display = ('user', 'bill_number', 'content_short', 'is_approved', 'likes_count', 'replies_count', 'created_at')
    list_filter = ('is_approved', 'is_edited', 'created_at', 'bill__status')
    search_fields = ('user__email', 'user__nickname', 'bill__title', 'bill__number', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'dislikes_count', 'replies_count')
    
    def bill_number(self, obj):
        return obj.bill.number
    bill_number.short_description = 'Numer projektu'
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Treść'
    
    fieldsets = (
        ('Komentarz', {
            'fields': ('user', 'bill', 'parent', 'content', 'is_approved', 'is_edited')
        }),
        ('Statystyki', {
            'fields': ('likes_count', 'dislikes_count', 'replies_count'),
            'classes': ('collapse',)
        }),
        ('Daty', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_comments', 'disapprove_comments', 'mark_as_edited']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} komentarzy zostało zatwierdzonych')
    approve_comments.short_description = 'Zatwierdź wybrane komentarze'
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} komentarzy zostało odrzuconych')
    disapprove_comments.short_description = 'Odrzuć wybrane komentarze'
    
    def mark_as_edited(self, request, queryset):
        queryset.update(is_edited=True)
        self.message_user(request, f'{queryset.count()} komentarzy zostało oznaczonych jako edytowane')
    mark_as_edited.short_description = 'Oznacz jako edytowane'


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    """Panel administracyjny dla polubień komentarzy"""
    list_display = ('user', 'comment_id', 'is_like', 'created_at')
    list_filter = ('is_like', 'created_at')
    search_fields = ('user__email', 'user__nickname', 'comment__content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def comment_id(self, obj):
        return obj.comment.id
    comment_id.short_description = 'ID komentarza'
    
    fieldsets = (
        ('Polubienie', {
            'fields': ('user', 'comment', 'is_like')
        }),
        ('Data', {
            'fields': ('created_at',)
        }),
    )


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    """Panel administracyjny dla zgłoszeń komentarzy"""
    list_display = ('user', 'comment_id', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('user__email', 'user__nickname', 'comment__content', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def comment_id(self, obj):
        return obj.comment.id
    comment_id.short_description = 'ID komentarza'
    
    fieldsets = (
        ('Zgłoszenie', {
            'fields': ('user', 'comment', 'reason', 'description', 'is_resolved')
        }),
        ('Data', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['resolve_reports', 'unresolve_reports']
    
    def resolve_reports(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, f'{queryset.count()} zgłoszeń zostało rozwiązanych')
    resolve_reports.short_description = 'Rozwiąż wybrane zgłoszenia'
    
    def unresolve_reports(self, request, queryset):
        queryset.update(is_resolved=False)
        self.message_user(request, f'{queryset.count()} zgłoszeń zostało nierozwiązanych')
    unresolve_reports.short_description = 'Oznacz jako nierozwiązane'

