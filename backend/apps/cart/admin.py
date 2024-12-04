from django.contrib import admin
from .models import Cart, CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'variant', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__email', 'variant__sku')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at', 'get_total_items')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'session_id')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return obj.get_total_quantity()
    get_total_items.short_description = 'Total Items'