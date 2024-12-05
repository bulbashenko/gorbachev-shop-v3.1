from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import ProductVariant
from apps.products.serializers import ProductVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.UUIDField(write_only=True, required=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_cost'
    )
    quantity = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'variant_id', 'quantity', 'total']
        read_only_fields = ['id', 'total']

    def validate(self, data):
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)

        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            # Check if variant is available based on stock
            if variant.stock <= 0:
                raise serializers.ValidationError({
                    "variant_id": "This product variant is out of stock."
                })
            if variant.stock < quantity:
                raise serializers.ValidationError({
                    "quantity": f"Only {variant.stock} items available."
                })
            data['variant'] = variant
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError({
                "variant_id": "Product variant not found."
            })

        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(
        read_only=True,
        source='get_total_quantity'
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        source='get_total_price'
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price']
        read_only_fields = ['id', 'total_items', 'total_price']