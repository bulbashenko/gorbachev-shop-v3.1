from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .base import BaseRequestSerializer, BaseResponseSerializer
from .product import ProductVariantResponseSerializer
from ..models import Cart, CartItem, ProductVariant
from decimal import Decimal
from typing import Optional

class CartItemRequestSerializer(BaseRequestSerializer):
    variant_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['variant_id', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }
    
    def validate(self, attrs):
        variant_id = attrs.get('variant_id')
        quantity = attrs.get('quantity', 1)

        try:
            variant = ProductVariant.objects.get(id=variant_id, is_active=True)
            if variant.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'error': 'exceeds available stock',
                    'detail': f'Only {variant.stock_quantity} items available'
                })
            
            # Check if adding to existing cart item would exceed stock
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                cart = Cart.objects.filter(user=request.user, is_active=True).first()
                if cart:
                    existing_item = cart.items.filter(variant=variant).first()
                    if existing_item:
                        total_quantity = existing_item.quantity + quantity
                        if total_quantity > variant.stock_quantity:
                            raise serializers.ValidationError({
                                'error': 'exceeds available stock',
                                'detail': f'Cannot add {quantity} more items. Only {variant.stock_quantity - existing_item.quantity} additional items available'
                            })
            
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError({
                'variant_id': 'Variant does not exist or is not active'
            })
        return attrs

class CartItemResponseSerializer(BaseResponseSerializer):
    variant = ProductVariantResponseSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_price(self, obj) -> Optional[Decimal]:
        if obj.id:
            return obj.total_price
        return None

class CartResponseSerializer(BaseResponseSerializer):
    items = CartItemResponseSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount', 'total_items', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_amount', 'total_items', 'item_count', 'created_at', 'updated_at']

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_total_amount(self, obj) -> Decimal:
        return obj.total_amount or Decimal('0.00')

    @extend_schema_field(serializers.IntegerField())
    def get_total_items(self, obj) -> int:
        return obj.total_items or 0

    @extend_schema_field(serializers.IntegerField())
    def get_item_count(self, obj) -> int:
        return obj.item_count or 0