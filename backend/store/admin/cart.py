from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import Cart, CartItem
from .mixins import ExportMixin, ActivationMixin, TimestampedAdminMixin

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = [
        'variant',
        'quantity',
        'total_price'
    ]
    readonly_fields = ['total_price']
    raw_id_fields = ['variant']

    def total_price(self, obj):
        if obj.id:
            return obj.total_price
        return _('N/A')
    total_price.short_description = _('Total Price')


@admin.register(Cart)
class CartAdmin(ExportMixin, ActivationMixin, TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'total_amount',
        'item_count',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'created_at',
        'user'
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    inlines = [CartItemInline]
    readonly_fields = [
        'total_amount',
        'created_at',
        'updated_at'
    ]
    actions = [
        'activate_items',
        'deactivate_items',
        'export_to_csv',
        'clear_carts'
    ]

    fieldsets = (
        (None, {
            'fields': ('user', 'total_amount')
        }),
        (_('Status and Timestamps'), {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = _('Items')

    def clear_carts(self, request, queryset):
        """Clear all items from selected carts."""
        for cart in queryset:
            cart.clear()
        self.message_user(
            request,
            _(f'Successfully cleared {queryset.count()} carts.')
        )
    clear_carts.short_description = _('Clear selected carts')

    def get_export_fields(self):
        return [
            'id',
            'user_email',
            'total_amount',
            'item_count',
            'is_active',
            'created_at'
        ]

    def get_user_email(self, obj):
        return obj.user.email


@admin.register(CartItem)
class CartItemAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'cart',
        'variant',
        'quantity',
        'total_price',
        'created_at'
    ]
    list_filter = [
        'cart__user',
        'created_at'
    ]
    search_fields = [
        'cart__user__email',
        'variant__sku',
        'variant__product__name'
    ]
    raw_id_fields = ['cart', 'variant']
    readonly_fields = [
        'total_price',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'cart',
                'variant',
                'quantity',
                'total_price'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_price(self, obj):
        if obj.id:
            return obj.total_price
        return _('N/A')
    total_price.short_description = _('Total Price')

    class Media:
        css = {
            'all': ('admin/css/cart.css',)
        }
        js = ('admin/js/cart.js',)