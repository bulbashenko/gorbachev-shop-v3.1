from rest_framework import serializers
from .base import BaseRequestSerializer, BaseResponseSerializer
from .product import ProductVariantResponseSerializer
from ..models import Order, OrderItem, Cart
from decimal import Decimal, InvalidOperation

class OrderItemRequestSerializer(BaseRequestSerializer):
    class Meta:
        model = OrderItem
        fields = ['quantity', 'price']
        extra_kwargs = {
            'price': {'required': True},
            'quantity': {'required': True, 'min_value': 1}
        }

    def validate_price(self, value):
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Invalid decimal value")

class OrderItemResponseSerializer(BaseResponseSerializer):
    variant = ProductVariantResponseSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'total_price']

class CreateOrderRequestSerializer(BaseRequestSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_method', 'notes']
        extra_kwargs = {
            'shipping_address': {'required': True, 'min_length': 1},
            'shipping_method': {'required': True, 'min_length': 1}
        }

    def validate(self, attrs):
        user = self.context['request'].user
        try:
            cart = Cart.objects.get(user=user, is_active=True)
            if not cart.items.exists():
                raise serializers.ValidationError({
                    "cart": "Cart is empty"
                })
            
            # Validate stock availability
            for cart_item in cart.items.all():
                if cart_item.quantity > cart_item.variant.stock_quantity:
                    raise serializers.ValidationError({
                        "items": f"Not enough stock for {cart_item.variant.product.name}. Available: {cart_item.variant.stock_quantity}"
                    })
        except Cart.DoesNotExist:
            raise serializers.ValidationError({
                "cart": "No active cart found"
            })
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(user=user, is_active=True)

        # Calculate total amount using Decimal
        total_amount = Decimal('0.00')
        for cart_item in cart.items.all():
            item_price = cart_item.variant.final_price
            total_amount += item_price * Decimal(str(cart_item.quantity))

        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            status='pending',
            **validated_data
        )

        # Create order items and update stock
        order_items = []
        for cart_item in cart.items.all():
            order_items.append(OrderItem(
                order=order,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.variant.final_price
            ))

            # Update stock
            cart_item.variant.stock_quantity -= cart_item.quantity
            cart_item.variant.save()

        # Bulk create order items
        OrderItem.objects.bulk_create(order_items)

        # Clear cart items and deactivate cart
        cart.items.all().delete()
        cart.is_active = False
        cart.save()

        return order

class UpdateOrderRequestSerializer(BaseRequestSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=False)

    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_method', 'tracking_number', 'notes', 'status', 'total_amount']
        extra_kwargs = {
            'shipping_address': {'required': True, 'min_length': 1},
            'shipping_method': {'required': True, 'min_length': 1}
        }

    def validate_total_amount(self, value):
        try:
            decimal_value = Decimal(str(value))
            if decimal_value <= 0:
                raise serializers.ValidationError("Total amount must be greater than 0")
            return decimal_value
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Invalid decimal value")

    def validate_status(self, value):
        instance = getattr(self, 'instance', None)
        if not instance:
            return value

        if instance.status == 'cancelled' and value != 'cancelled':
            raise serializers.ValidationError("Cannot change status of cancelled order")
        if instance.status == 'delivered' and value != 'delivered':
            raise serializers.ValidationError("Cannot change status of delivered order")
        if instance.status == 'refunded' and value != 'refunded':
            raise serializers.ValidationError("Cannot change status of refunded order")
        return value

class OrderResponseSerializer(BaseResponseSerializer):
    items = OrderItemResponseSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'total_amount',
            'shipping_address', 'shipping_method', 'tracking_number',
            'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status_display', 'created_at', 'updated_at']