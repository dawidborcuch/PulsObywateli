from django.contrib import admin
from .models import Bill, BillVote, BillUpdate


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Panel administracyjny dla projektów ustaw"""
    list_display = ('number', 'title_short', 'status', 'submission_date', 'total_votes', 'support_percentage', 'is_active', 'is_featured')
    list_filter = ('status', 'is_active', 'is_featured', 'submission_date', 'created_at')
    search_fields = ('title', 'number', 'authors', 'description')
    ordering = ('-submission_date', '-created_at')
    readonly_fields = ('created_at', 'updated_at', 'support_votes', 'against_votes', 'neutral_votes', 'total_votes')
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('title', 'description', 'number', 'status', 'submission_date')
        }),
        ('Autorzy', {
            'fields': ('authors', 'initiators')
        }),
        ('Linki', {
            'fields': ('source_url', 'document_url')
        }),
        ('Statystyki', {
            'fields': ('support_votes', 'against_votes', 'neutral_votes', 'total_votes'),
            'classes': ('collapse',)
        }),
        ('Opcje', {
            'fields': ('is_active', 'is_featured', 'tags')
        }),
        ('Daty', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Tytuł'
    
    def support_percentage(self, obj):
        return f"{obj.support_percentage}%"
    support_percentage.short_description = 'Poparcie %'
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'activate_bills', 'deactivate_bills']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} projektów zostało wyróżnionych')
    mark_as_featured.short_description = 'Wyróżnij wybrane projekty'
    
    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f'{queryset.count()} projektów zostało odznaczonych')
    mark_as_not_featured.short_description = 'Odznacz wybrane projekty'
    
    def activate_bills(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} projektów zostało aktywowanych')
    activate_bills.short_description = 'Aktywuj wybrane projekty'
    
    def deactivate_bills(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} projektów zostało dezaktywowanych')
    deactivate_bills.short_description = 'Dezaktywuj wybrane projekty'


@admin.register(BillVote)
class BillVoteAdmin(admin.ModelAdmin):
    """Panel administracyjny dla głosów na projekty ustaw"""
    list_display = ('user', 'bill_number', 'vote', 'created_at')
    list_filter = ('vote', 'created_at', 'bill__status')
    search_fields = ('user__email', 'user__nickname', 'bill__title', 'bill__number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def bill_number(self, obj):
        return obj.bill.number
    bill_number.short_description = 'Numer projektu'
    
    fieldsets = (
        ('Głos', {
            'fields': ('user', 'bill', 'vote')
        }),
        ('Daty', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BillUpdate)
class BillUpdateAdmin(admin.ModelAdmin):
    """Panel administracyjny dla aktualizacji projektów ustaw"""
    list_display = ('bill_number', 'old_status', 'new_status', 'created_at')
    list_filter = ('old_status', 'new_status', 'created_at')
    search_fields = ('bill__title', 'bill__number', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def bill_number(self, obj):
        return obj.bill.number
    bill_number.short_description = 'Numer projektu'
    
    fieldsets = (
        ('Aktualizacja', {
            'fields': ('bill', 'old_status', 'new_status', 'description')
        }),
        ('Data', {
            'fields': ('created_at',)
        }),
    )

