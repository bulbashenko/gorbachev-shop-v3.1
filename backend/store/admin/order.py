from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from ..models import Order, OrderItem
from .mixins import ExportMixin, TimestampedAdminMixin

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    raw_id_fields = ['variant']
    fields = [
        'variant',
        'quantity',
        'price',
        'total_price'
    ]

    def total_price(self, obj):
        if obj.id:
            return obj.total_price
        return _('N/A')
    total_price.short_description = _('Total Price')


@admin.register(Order)
class OrderAdmin(ExportMixin, TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'status',
        'total_amount',
        'created_at',
        'order_actions'
    ]
    list_filter = [
        'status',
        'created_at',
        'shipping_method'
    ]
    search_fields = [
        'id',
        'user__email',
        'shipping_address',
        'tracking_number'
    ]
    readonly_fields = [
        'total_amount',
        'created_at',
        'updated_at'
    ]
    inlines = [OrderItemInline]
    actions = [
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'export_to_csv'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'status',
                'total_amount'
            )
        }),
        (_('Shipping Information'), {
            'fields': (
                'shipping_address',
                'shipping_method',
                'tracking_number'
            )
        }),
        (_('Additional Information'), {
            'fields': (
                'notes',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def order_actions(self, obj):
        """Generate action buttons for the order."""
        view_url = reverse('admin:store_order_change', args=[obj.pk])
        print_url = f"{view_url}?print=true"
        
        return format_html(
            '<div class="order-actions">'
            '<a class="button" href="{}">{}</a>&nbsp;'
            '<a class="button" href="{}">{}</a>'
            '</div>',
            view_url, _('View'),
            print_url, _('Print')
        )
    order_actions.short_description = _('Actions')

    def mark_as_processing(self, request, queryset):
        """Mark selected orders as processing."""
        updated = queryset.filter(status='pending').update(status='processing')
        self.message_user(
            request,
            _(f'{updated} orders marked as processing.')
        )
    mark_as_processing.short_description = _("Mark selected orders as processing")

    def mark_as_shipped(self, request, queryset):
        """Mark selected orders as shipped."""
        updated = queryset.filter(status='processing').update(status='shipped')
        self.message_user(
            request,
            _(f'{updated} orders marked as shipped.')
        )
    mark_as_shipped.short_description = _("Mark selected orders as shipped")

    def mark_as_delivered(self, request, queryset):
        """Mark selected orders as delivered."""
        updated = queryset.filter(status='shipped').update(status='delivered')
        self.message_user(
            request,
            _(f'{updated} orders marked as delivered.')
        )
    mark_as_delivered.short_description = _("Mark selected orders as delivered")

    def get_export_fields(self):
        """Specify fields for CSV export."""
        return [
            'id',
            'user_email',
            'status',
            'total_amount',
            'shipping_method',
            'tracking_number',
            'created_at'
        ]

    def get_user_email(self, obj):
        return obj.user.email

    class Media:
        css = {
            'all': ('admin/css/order.css',)
        }
        js = ('admin/js/order.js',)


@admin.register(OrderItem)
class OrderItemAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'order',
        'variant',
        'quantity',
        'price',
        'total_price',
        'created_at'
    ]
    list_filter = [
        'order__status',
        'created_at'
    ]
    search_fields = [
        'order__id',
        'variant__sku',
        'variant__product__name'
    ]
    raw_id_fields = [
        'order',
        'variant'
    ]
    readonly_fields = [
        'total_price',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'order',
                'variant',
                'quantity',
                'price',
                'total_price'
            )
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def total_price(self, obj):
        if obj.id:
            return obj.total_price
        return _('N/A')
    total_price.short_description = _('Total Price')