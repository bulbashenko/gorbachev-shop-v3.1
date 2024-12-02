from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.categories.models import Category
from django.db.models import Sum, Q
import uuid

class Size(models.Model):
    name = models.CharField(max_length=10)  # S, M, L, XL, etc.
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)  # HEX code

    def __str__(self):
        return self.name

class Product(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
        ('U', 'Unisex'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    description = models.TextField(_('Description'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    brand = models.CharField(max_length=100)
    
    # Цены и скидки
    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2
    )
    sale_price = models.DecimalField(
        _('Sale Price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Характеристики
    material = models.CharField(max_length=100, blank=True)
    care_instructions = models.TextField(blank=True)
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'slug']),
            models.Index(fields=['price', 'sale_price']),
            models.Index(fields=['brand', 'gender']),
        ]

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.price

    def get_available_sizes(self):
        """Получение доступных размеров"""
        return Size.objects.filter(
            productvariant__product=self,
            productvariant__stock__gt=0
        ).distinct()

    def get_available_colors(self):
        """Получение доступных цветов"""
        return Color.objects.filter(
            productvariant__product=self,
            productvariant__stock__gt=0
        ).distinct()

    def get_total_stock(self):
        """Получение общего количества товара"""
        return self.variants.aggregate(
            total=Sum('stock')
        )['total'] or 0

    def is_available(self):
        """Проверка наличия товара"""
        return self.get_total_stock() > 0

    def get_main_image(self, color=None):
        """Получение главного изображения"""
        if color:
            image = self.images.filter(
                color=color,
                is_main=True
            ).first()
            if image:
                return image
        return self.images.filter(is_main=True).first()

    def check_variant_availability(self, size, color):
        """Проверка наличия конкретного варианта"""
        try:
            variant = self.variants.get(size=size, color=color)
            return variant.stock > 0, variant.stock
        except ProductVariant.DoesNotExist:
            return False, 0

    def get_discount_percentage(self):
        """Получение процента скидки"""
        if self.sale_price and self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount, 2)
        return 0

class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('product', 'size', 'color')
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['stock']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

    @property
    def stock_available(self):
        return self.stock > 0

    def decrease_stock(self, quantity):
        """Уменьшение остатка"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        """Увеличение остатка"""
        self.stock += quantity
        self.save()

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='products/')
    is_main = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_main']),
        ]

    def save(self, *args, **kwargs):
        if self.is_main:
            # Сбрасываем флаг main для других изображений того же товара и цвета
            ProductImage.objects.filter(
                product=self.product,
                color=self.color,
                is_main=True
            ).update(is_main=False)
        super().save(*args, **kwargs)