from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.contrib.admin.helpers import ActionForm
from django import forms
import csv
from datetime import datetime
from .models import Order, OrderItem, OrderStatus

class OrderActionForm(ActionForm):
    """Форма для массовых действий с заказами"""
    status = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + list(Order.OrderStatus.choices),
        label='Изменить статус на'
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_image', 'product_name', 'get_total', 'get_profit')
    fields = (
        'get_image', 'product_name', 'variant',
        'quantity', 'price', 'get_total', 'get_profit'
    )
    
    def get_image(self, obj):
        if obj.variant.product.images.filter(is_main=True).exists():
            img = obj.variant.product.images.filter(is_main=True).first()
            return mark_safe(f'<img src="{img.image.url}" width="50" />')
        return '-'
    get_image.short_description = 'Изображение'
    
    def product_name(self, obj):
        return obj.variant.product.name
    product_name.short_description = 'Товар'
    
    def get_total(self, obj):
        if obj and obj.price is not None and obj.quantity is not None:
            return obj.price * obj.quantity
        return "-"


    get_total.short_description = 'Итого'

    def get_profit(self, obj):
        if hasattr(obj.variant.product, 'cost_price'):
            return (obj.price - obj.variant.product.cost_price) * obj.quantity
        return '-'
    get_profit.short_description = 'Прибыль'

class OrderStatusInline(admin.TabularInline):
    model = OrderStatus
    extra = 0
    readonly_fields = ('created_at', 'created_by')
    fields = ('status', 'notes', 'created_at', 'created_by')
    ordering = ('-created_at',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 
        'created_at',
        'get_customer_info',
        'total', 
        'status', 
        'payment_status',
        'shipping_method',
        'payment_link'
    )
    list_filter = (
        'status', 
        'payment_status', 
        'shipping_method',
        'created_at', 
        'paid_at', 
        'shipped_at'
    )
    search_fields = (
        'order_number', 
        'user__email', 
        'user__first_name',
        'user__last_name', 
        'shipping_address__full_name',
        'shipping_address__phone'
    )
    readonly_fields = (
        'order_number', 
        'created_at', 
        'updated_at',
        'paid_at', 
        'shipped_at', 
        'delivered_at',
        'get_customer_orders',
        'get_customer_total',
        'get_summary'
    )
    inlines = [OrderItemInline, OrderStatusInline]
    action_form = OrderActionForm
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                ('order_number', 'status', 'payment_status'),
                ('created_at', 'updated_at'),
                ('paid_at', 'shipped_at', 'delivered_at'),
            )
        }),
        ('Клиент', {
            'fields': (
                ('user', 'get_customer_orders', 'get_customer_total'),
                ('email', 'phone'),
            )
        }),
        ('Доставка', {
            'fields': (
                'shipping_method',
                'shipping_address',
                'shipping_cost',
                'tracking_number',
            )
        }),
        ('Оплата', {
            'fields': (
                'subtotal',
                'tax',
                'total',
                'get_summary'
            )
        }),
        ('Дополнительно', {
            'fields': (
                'customer_notes',
                'staff_notes',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_customer_info(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}">{}</a><br/>{}<br/>{}',
                url,
                obj.user.get_full_name() or obj.user.email,
                obj.phone,
                obj.email
            )
        return f'{obj.email}<br/>{obj.phone}'
    get_customer_info.short_description = 'Клиент'
    get_customer_info.allow_tags = True

    def payment_link(self, obj):
        if hasattr(obj, 'payment'):
            url = reverse('admin:payments_payment_change', args=[obj.payment.id])
            status_colors = {
                'pending': 'orange',
                'paid': 'green',
                'failed': 'red',
                'refunded': 'gray'
            }
            color = status_colors.get(obj.payment.status, 'black')
            return format_html(
                '<a href="{}" style="color: {};">{}</a>',
                url,
                color,
                obj.payment.get_status_display()
            )
        return '-'
    payment_link.short_description = 'Платеж'

    def get_customer_orders(self, obj):
        if obj.user:
            orders = Order.objects.filter(user=obj.user).exclude(id=obj.id)
            return format_html(
                'Всего заказов: {}<br/>Выполнено: {}<br/>Отменено: {}',
                orders.count(),
                orders.filter(status=Order.OrderStatus.DELIVERED).count(),
                orders.filter(status=Order.OrderStatus.CANCELLED).count()
            )
        return 'Гостевой заказ'
    get_customer_orders.short_description = 'История клиента'

    def get_customer_total(self, obj):
        if obj.user:
            total = Order.objects.filter(
                user=obj.user,
                status=Order.OrderStatus.DELIVERED
            ).aggregate(
                total=Sum('total')
            )['total'] or 0
            return f"{total:.2f}"
        return '-'
    get_customer_total.short_description = 'Общая сумма покупок'

    def get_summary(self, obj):
        items = obj.items.all()
        return format_html(
            'Товаров: {}<br/>Средний чек: {:.2f}<br/>Вес: {} кг',
            items.count(),
            obj.total,
            sum(item.variant.product.weight * item.quantity 
                for item in items if hasattr(item.variant.product, 'weight'))
        )
    get_summary.short_description = 'Сводка по заказу'