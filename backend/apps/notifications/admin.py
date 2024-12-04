from django.contrib import admin
from django.utils.html import format_html
from .models import EmailTemplate, EmailLog

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at', 'updated_at')
    search_fields = ('name', 'subject', 'html_content', 'text_content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'subject')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        'recipient_email',
        'subject',
        'template',
        'status',
        'sent_at',
        'created_at'
    )
    list_filter = ('status', 'template', 'created_at', 'sent_at')
    search_fields = ('recipient_email', 'subject', 'error_message')
    readonly_fields = (
        'recipient',
        'recipient_email',
        'subject',
        'template',
        'context',
        'status',
        'error_message',
        'sent_at',
        'created_at'
    )
    
    fieldsets = (
        (None, {
            'fields': (
                'recipient',
                'recipient_email',
                'subject',
                'template'
            )
        }),
        ('Details', {
            'fields': (
                'status',
                'context',
                'error_message'
            )
        }),
        ('Timestamps', {
            'fields': (
                'sent_at',
                'created_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False