from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from apps.products.models import ProductVariant
import uuid

User = get_user_model()

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        AWAITING_PAYMENT = 'awaiting_payment', _('Awaiting Payment')
        PROCESSING = 'processing', _('Processing')
        CONFIRMED = 'confirmed', _('Confirmed')
        ASSEMBLING = 'assembling', _('Assembling')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')
        RETURNED = 'returned', _('Returned')

    class ShippingMethod(models.TextChoices):
        STANDARD = 'standard', _('Standard Delivery (2-4 days)')
        EXPRESS = 'express', _('Express Delivery (1-2 days)')
        PICKUP = 'pickup', _('Pickup from Store')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.AWAITING_PAYMENT
    )
    
    # Контактная информация
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Адреса
    shipping_address = models.ForeignKey(
        'users.UserAddress',
        related_name='shipping_orders',
        on_delete=models.PROTECT
    )
    billing_address = models.ForeignKey(
        'users.UserAddress',
        related_name='billing_orders',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    # Доставка
    shipping_method = models.CharField(
        max_length=20,
        choices=ShippingMethod.choices,
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    # Суммы
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Статусы
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Комментарии
    customer_notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-created_at').first()
            if last_order:
                last_number = int(last_order.order_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.order_number = f'ORD{new_number:06d}'
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'variant')
    
    def get_total(self):
        return self.price * self.quantity

class OrderStatus(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='status_history',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=Order.OrderStatus.choices
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-created_at']