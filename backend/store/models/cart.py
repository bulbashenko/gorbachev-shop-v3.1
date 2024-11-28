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

class Cart(BaseModel):
    """Shopping cart model."""
    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
        related_name='carts'
    )
    total_amount = models.DecimalField(
        _('Total amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def calculate_total(self):
        """Calculate the total amount for all items in the cart."""
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount', 'updated_at'])
        return total

    @property
    def total_items(self):
        """Get the total number of unique items in the cart."""
        return self.items.count()

    @property
    def item_count(self):
        """Get the total quantity of all items in the cart."""
        return sum(item.quantity for item in self.items.all())

    @transaction.atomic
    def add_item(self, variant, quantity=1):
        """Add an item to the cart or update its quantity if it already exists."""
        if not self.is_active:
            raise ValidationError(_("Cannot add items to inactive cart"))

        if quantity <= 0:
            raise ValidationError(_("Quantity must be positive"))
        
        if not variant.is_active or not variant.product.is_active:
            raise ValidationError(_("Product is not available"))
            
        if quantity > variant.stock_quantity:
            raise ValidationError(_("Requested quantity exceeds available stock"))

        cart_item, created = self.items.get_or_create(
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > variant.stock_quantity:
                raise ValidationError(_("Requested quantity exceeds available stock"))
            cart_item.save()

        self.calculate_total()
        logger.info(f"Added {quantity} of {variant.sku} to cart {self.id}")
        return cart_item

    @transaction.atomic
    def update_item(self, variant, quantity):
        """Update the quantity of an item in the cart."""
        if not self.is_active:
            raise ValidationError(_("Cannot update items in inactive cart"))

        try:
            cart_item = self.items.get(variant=variant)
            if quantity <= 0:
                cart_item.delete()
                self.calculate_total()
                logger.info(f"Removed {variant.sku} from cart {self.id}")
                return None
            
            if not variant.is_active or not variant.product.is_active:
                raise ValidationError(_("Product is not available"))
                
            if quantity > variant.stock_quantity:
                raise ValidationError(_("Requested quantity exceeds available stock"))
            
            cart_item.quantity = quantity
            cart_item.save()
            self.calculate_total()
            logger.info(f"Updated {variant.sku} quantity to {quantity} in cart {self.id}")
            return cart_item
        except CartItem.DoesNotExist:
            if quantity <= 0:
                return None
            return self.add_item(variant, quantity)

    @transaction.atomic
    def clear(self):
        """Remove all items from the cart."""
        self.items.all().delete()
        self.total_amount = Decimal('0.00')
        self.save(update_fields=['total_amount', 'updated_at'])
        logger.info(f"Cleared cart {self.id}")

    def __str__(self):
        return f"Cart {self.id} - {self.user.email}"

class CartItem(BaseModel):
    """Individual item in a shopping cart."""
    cart = models.ForeignKey(
        Cart,
        verbose_name=_('Cart'),
        related_name='items',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_('Product Variant'),
        related_name='cart_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=1
    )

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = [['cart', 'variant']]
        indexes = [
            models.Index(fields=['cart', 'variant']),
        ]

    @property
    def total_price(self):
        """Calculate the total price for this cart item."""
        return self.variant.final_price * Decimal(str(self.quantity))

    @property
    def product(self):
        """Get the product associated with this cart item."""
        return self.variant.product

    def clean(self):
        """Validate the cart item."""
        super().clean()
        if not self.cart.is_active:
            raise ValidationError(_("Cannot modify items in inactive cart"))
            
        if not self.variant.is_active or not self.variant.product.is_active:
            raise ValidationError(_("Product is not available"))

        if self.quantity > self.variant.stock_quantity:
            raise ValidationError({'quantity': _("Requested quantity exceeds available stock")
        })

    def save(self, *args, **kwargs):
        """Save the cart item with validation."""
        self.full_clean()
        super().save(*args, **kwargs)
        if self.cart:
            self.cart.calculate_total()

    def delete(self, *args, **kwargs):
        """Delete the cart item and update cart total."""
        cart = self.cart
        super().delete(*args, **kwargs)
        if cart:
            cart.calculate_total()

    def __str__(self):
        return f"{self.quantity}x {self.variant.product.name} ({self.variant.sku})"