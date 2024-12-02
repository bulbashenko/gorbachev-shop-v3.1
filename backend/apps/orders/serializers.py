from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order, OrderItem, OrderStatus
from apps.users.models import UserAddress
from apps.payments.models import Payment

User = get_user_model()

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='variant.product.name')
    product_image = serializers.ImageField(source='variant.product.images.first.image')
    size = serializers.CharField(source='variant.size.name')
    color = serializers.CharField(source='variant.color.name')
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='get_total'
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'variant', 'product_name', 'product_image',
            'size', 'color', 'quantity', 'price', 'total'
        ]

class OrderStatusSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = OrderStatus
        fields = ['status', 'notes', 'created_at', 'created_by']

class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.all()
    )
    billing_address = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.all(),
        required=False
    )
    shipping_method = serializers.ChoiceField(
        choices=Order.ShippingMethod.choices  # Fixed: Using proper ShippingMethod choices
    )
    payment_method = serializers.ChoiceField(
        choices=Payment.PaymentMethod.choices  # Fixed: Using proper PaymentMethod choices
    )
    customer_notes = serializers.CharField(
        required=False,
        allow_blank=True
    )

class OrderTrackingSerializer(serializers.ModelSerializer):
    status_history = OrderStatusSerializer(many=True, read_only=True)
    current_status = serializers.CharField(source='status')
    shipping_address = serializers.CharField(source='shipping_address.__str__', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'order_number', 'current_status', 'status_history',
            'tracking_number', 'shipping_method', 'shipping_address',
            'created_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusSerializer(many=True, read_only=True)
    shipping_address_details = serializers.CharField(
        source='shipping_address.__str__',
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'email', 'phone',
            'shipping_address', 'shipping_address_details',
            'billing_address', 'shipping_method', 'shipping_cost',
            'tracking_number', 'subtotal', 'tax', 'total',
            'payment_status', 'items', 'status_history',
            'customer_notes', 'created_at', 'paid_at',
            'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax',
            'total', 'payment_status', 'created_at',
            'paid_at', 'shipped_at', 'delivered_at'
        ]