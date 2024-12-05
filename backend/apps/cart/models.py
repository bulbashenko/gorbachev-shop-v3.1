from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import ProductVariant
import uuid

User = get_user_model()

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False) |
                    models.Q(session_id__isnull=False)
                ),
                name='cart_user_or_session'
            )
        ]

    def get_total_price(self):
        """Вычисляет общую стоимость всех товаров в корзине"""
        total = sum(item.get_cost() for item in self.items.all())
        return round(total, 2) if total else 0
    
    def get_total_quantity(self):
        """Вычисляет общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    def transfer_to_user(self, user):
        """Переносит корзину от гостя к пользователю"""
        if user.is_authenticated and self.session_id:
            try:
                user_cart = Cart.objects.get(user=user)
                # Переносим товары из гостевой корзины
                for item in self.items.all():
                    existing_item = user_cart.items.filter(variant=item.variant).first()
                    if existing_item:
                        # Если товар уже есть в корзине пользователя, обновляем количество
                        existing_item.quantity += item.quantity
                        if existing_item.quantity > item.variant.stock:
                            existing_item.quantity = item.variant.stock
                        existing_item.save()
                    else:
                        # Если товара нет, просто переносим его
                        item.cart = user_cart
                        item.save()
                self.delete()
            except Cart.DoesNotExist:
                # Если у пользователя нет корзины, просто привязываем гостевую корзину к нему
                self.user = user
                self.session_id = None
                self.save()

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'variant')

    def get_cost(self):
        """Вычисляет стоимость данного товара в корзине"""
        return self.variant.product.current_price * self.quantity

    def is_available(self):
        """Проверяет, доступен ли товар в запрошенном количестве"""
        return self.variant.stock >= self.quantity

    def save(self, *args, **kwargs):
        """
        Переопределяем сохранение, чтобы количество товара не превышало 
        доступное на складе
        """
        if self.quantity > self.variant.stock:
            self.quantity = self.variant.stock
        super().save(*args, **kwargs)
