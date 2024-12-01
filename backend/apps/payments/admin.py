from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order', 'amount', 'payment_method',
        'status', 'transaction_id', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'order', 'amount', 'payment_method',
                'status', 'transaction_id'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )