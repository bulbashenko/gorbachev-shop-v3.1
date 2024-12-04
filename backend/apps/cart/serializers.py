from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import ProductVariant
from apps.products.serializers import ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.UUIDField(write_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_cost'
    )

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'variant_id', 'quantity', 'total']
        read_only_fields = ['id', 'total']

    def validate(self, data):
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)
        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError({
                "variant_id": "Product variant not found."
            })

        if variant.stock < quantity:
            raise serializers.ValidationError({
                "quantity": f"Only {variant.stock} items available."
            })

        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_total_price'
    )
    total_items = serializers.IntegerField(
        read_only=True,
        source='get_total_quantity'
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items']
        read_only_fields = ['id', 'total_price', 'total_items']