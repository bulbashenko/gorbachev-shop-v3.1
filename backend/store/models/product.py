from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal
from django.conf import settings
from django.db import transaction

from .base import BaseModel
from .category import Category

class ProductAttribute(BaseModel):
    """Model for defining product attributes like size, color, etc."""
    name = models.CharField(_('Name'), max_length=50)
    values = ArrayField(
        models.CharField(max_length=50),
        verbose_name=_('Possible values')
    )

    class Meta:
        verbose_name = _('Product Attribute')
        verbose_name_plural = _('Product Attributes')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({', '.join(self.values)})"

class Product(BaseModel):
    """Main product model."""
    category = models.ForeignKey(
        Category,
        verbose_name=_('Category'),
        related_name='products',
        on_delete=models.CASCADE
    )
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'))
    base_price = models.DecimalField(
        _('Base price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    meta_title = models.CharField(_('Meta title'), max_length=150, blank=True)
    meta_description = models.TextField(_('Meta description'), blank=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not self.category.is_active:
            raise ValidationError(_("Cannot assign product to inactive category"))

    @property
    def main_image(self):
        """Get the main product image."""
        return self.images.filter(type='main', is_active=True).first()

    @property
    def gallery_images(self):
        """Get all gallery images."""
        return self.images.filter(type='gallery', is_active=True)

    @property
    def available_variants(self):
        """Get all active variants with stock."""
        return self.variants.filter(is_active=True, stock_quantity__gt=0)

class ProductVariant(BaseModel):
    """Model for product variants (e.g., different sizes/colors)."""
    product = models.ForeignKey(
        Product,
        verbose_name=_('Product'),
        related_name='variants',
        on_delete=models.CASCADE
    )
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    attributes = models.JSONField(
        _('Attributes'),
        help_text=_('JSON object containing attribute values, e.g., {"size": "M", "color": "Red"}')
    )
    price_adjustment = models.DecimalField(
        _('Price adjustment'),
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Amount to add to or subtract from base price')
    )
    stock_quantity = models.IntegerField(
        _('Stock quantity'),
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['product', 'is_active']),
        ]
        unique_together = [['product', 'attributes']]

    def __str__(self):
        attrs = ', '.join(f"{k}: {v}" for k, v in self.attributes.items())
        return f"{self.product.name} - {attrs}"

    def clean(self):
        super().clean()
        if self.price_adjustment and self.price_adjustment < 0:
            if abs(self.price_adjustment) > self.product.base_price:
                raise ValidationError(_("Price adjustment cannot exceed base price"))
        
        if not self.product.is_active:
            raise ValidationError(_("Cannot create variant for inactive product"))

    @property
    def final_price(self):
        """Calculate the final price including adjustments."""
        return self.product.base_price + self.price_adjustment

    @transaction.atomic
    def update_stock(self, quantity_change, user=None, note=None):
        """Update stock quantity with validation and history tracking."""
        if quantity_change == 0:
            return self.stock_quantity

        old_quantity = self.stock_quantity
        new_quantity = max(0, old_quantity + quantity_change)
        
        if new_quantity != old_quantity:
            self.stock_quantity = new_quantity
            self.save()

            StockHistory.objects.create(
                variant=self,
                user=user,
                old_quantity=old_quantity,
                new_quantity=new_quantity,
                change_amount=quantity_change,
                note=note or _('Stock update')
            )

        return new_quantity

class ProductImage(BaseModel):
    """Model for product images."""
    TYPES = (
        ('main', _('Main')),
        ('gallery', _('Gallery')),
        ('variant', _('Variant')),
    )

    product = models.ForeignKey(
        Product,
        verbose_name=_('Product'),
        related_name='images',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_('Product Variant'),
        null=True,
        blank=True,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        _('Image'),
        upload_to='products/%Y/%m/%d'
    )
    alt_text = models.CharField(_('Alt text'), max_length=200)
    type = models.CharField(
        _('Image type'),
        max_length=10,
        choices=TYPES,
        default='gallery'
    )
    order = models.IntegerField(_('Display order'), default=0)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'type', 'is_active']),
            models.Index(fields=['variant', 'is_active']),
        ]
        unique_together = [['product', 'type']] # Ensures only one main image per product

    def clean(self):
        super().clean()
        if self.type == 'variant' and not self.variant:
            raise ValidationError(_("Variant image must be associated with a variant"))
        if self.type == 'main' and ProductImage.objects.exclude(pk=self.pk).filter(
            product=self.product, 
            type='main',
            is_active=True
        ).exists():
            raise ValidationError(_("Product already has a main image"))

    def __str__(self):
        base = f"Image for {self.product.name}"
        if self.variant:
            return f"{base} ({self.variant.sku})"
        return f"{base} ({self.type})"

class StockHistory(BaseModel):
    """Model for tracking stock changes."""
    variant = models.ForeignKey(
        ProductVariant,
        verbose_name=_('Product Variant'),
        related_name='stock_history',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='stock_updates'
    )
    old_quantity = models.IntegerField(_('Old quantity'))
    new_quantity = models.IntegerField(_('New quantity'))
    change_amount = models.IntegerField(_('Change amount'))
    note = models.CharField(_('Note'), max_length=255)

    class Meta:
        verbose_name = _('Stock History')
        verbose_name_plural = _('Stock History')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.variant.sku} - {self.change_amount:+d} ({self.created_at})"

    @property
    def is_increase(self):
        """Check if this was a stock increase."""
        return self.change_amount > 0

    @property
    def is_decrease(self):
        """Check if this was a stock decrease."""
        return self.change_amount < 0