from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from decimal import Decimal
import logging

from .base import BaseModel
from .product import ProductVariant
from users.models import User

logger = logging.getLogger(__name__)

class Order(BaseModel):
    """Order model for tracking customer purchases."""
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    )

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        related_name='orders',
        on_delete=models.PROTECT
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_amount = models.DecimalField(
        _('Total amount'),
        max_digits=10,
        decimal_places=2
    )
    shipping_address = models.TextField(_('Shipping address'))
    shipping_method = models.CharField(_('Shipping method'), max_length=50)
    tracking_number = models.CharField(
        _('Tracking number'),
        max_length=100,
        blank=True
    )
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.user.email} ({self.status})"

    def calculate_total(self):
        """Calculate the total amount for all items in the order."""
        return sum(item.total_price for item in self.items.all())

    def clean(self):
        """Validate the order."""
        super().clean()
        if not self.status in dict(self.STATUS_CHOICES):
            raise ValidationError({
                'status': _("Invalid status value")
            })

        if not self.total_amount or self.total_amount <= 0:
            raise ValidationError({
                'total_amount': _("Total amount must be greater than zero")
            })

    @transaction.atomic
    def create_from_cart(self, cart):
        """Create an order from a cart."""
        if not cart.items.exists():
            raise ValidationError(_("Cannot create order from empty cart"))
            
        # Validate stock for all items
        for item in cart.items.all():
            if item.quantity > item.variant.stock_quantity:
                raise ValidationError(_(
                    f"Not enough stock for {item.variant.product.name}"
                ))
                
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=self,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.variant.final_price
            )
            
            # Update stock
            cart_item.variant.update_stock(
                -cart_item.quantity,
                user=self.user,
                note=f"Order {self.id}"
            )
            
        # Clear cart
        cart.clear()
        
        # Calculate total
        self.total_amount = self.calculate_total()
        self.save()
        
        logger.info(f"Created order {self.id} from cart {cart.id}")

    @transaction.atomic
    def update_status(self, new_status):
        """Update order status with validation."""
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValidationError(_("Invalid status"))
        
        old_status = self.status
        self.status = new_status
        self.full_clean()
        self.save()
        
        logger.info(f"Order {self.id} status changed from {old_status} to {new_status}")
        
        # If order is cancelled, return items to stock
        if new_status == 'cancelled' and old_status != 'cancelled':
            self._return_items_to_stock()

    def _return_items_to_stock(self):
        """Return ordered items back to stock."""
        for item in self.items.all():
            item.variant.update_stock(
                item.quantity,
                user=self.user,
                note=f"Returned from cancelled order {self.id}"
            )

    def can_cancel(self):
        """Check if the order can be cancelled."""
        return self.status in ['pending', 'confirmed']

    @transaction.atomic
    def cancel(self):
        """Cancel the order if possible."""
        if not self.can_cancel():
            raise ValidationError(_("Order cannot be cancelled"))
        self.update_status('cancelled')

    def save(self, *args, **kwargs):
        """Save the order with validation."""
        if not self.total_amount:
            self.total_amount = self.calculate_total()
        self.full_clean()
        super().save(*args, **kwargs)


class OrderItem(BaseModel):
    """Individual item in an order."""
    order = models.ForeignKey(
        Order,
        verbose_name=_('Order'),
        related_name='items',
        on_delete=models.PROTECT
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_('Product Variant'),
        related_name='order_items',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(_('Quantity'))
    price = models.DecimalField(
        _('Price at time of purchase'),
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        indexes = [
            models.Index(fields=['order', 'variant']),
        ]

    @property
    def total_price(self):
        """Calculate the total price for this order item."""
        return self.price * Decimal(str(self.quantity))

    def clean(self):
        """Validate the order item."""
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({
                'quantity': _("Quantity must be positive")
            })
        
        if self.variant and self.quantity > self.variant.stock_quantity and self.order.status == 'pending':
            raise ValidationError({
                'quantity': _("Requested quantity exceeds available stock")
            })

        if self.price <= 0:
            raise ValidationError({
                'price': _("Price must be greater than zero")
            })

    def save(self, *args, **kwargs):
        """Save the order item with validation."""
        if not self.price and self.variant:
            self.price = self.variant.final_price
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order.id} - {self.variant.product.name} ({self.variant.sku})"