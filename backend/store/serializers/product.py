from rest_framework import serializers
from .base import BaseRequestSerializer, BaseResponseSerializer
from .category import CategoryResponseSerializer
from ..models import Product, ProductVariant, ProductImage
from typing import Dict, Optional, Any
from drf_spectacular.utils import extend_schema_field

class ProductImageRequestSerializer(BaseRequestSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'type', 'order', 'variant']
        extra_kwargs = {
            'alt_text': {'min_length': 1}
        }

class ProductImageResponseSerializer(BaseResponseSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'type', 'order', 'variant']
        read_only_fields = ['id']

class ProductVariantRequestSerializer(BaseRequestSerializer):
    class Meta:
        model = ProductVariant
        fields = ['sku', 'attributes', 'price_adjustment', 'stock_quantity', 'is_active']
        extra_kwargs = {
            'sku': {'min_length': 1},
            'attributes': {'required': True}
        }

    def validate_sku(self, value):
        if self.instance is None and ProductVariant.objects.filter(sku=value).exists():
            raise serializers.ValidationError("SKU must be unique")
        return value

class ProductVariantResponseSerializer(BaseResponseSerializer):
    images = ProductImageResponseSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'attributes', 'price_adjustment',
            'stock_quantity', 'is_active', 'final_price', 'images'
        ]
        read_only_fields = ['id', 'final_price']

class ProductRequestSerializer(BaseRequestSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = [
            'category_id', 'name', 'slug', 'description', 'base_price',
            'is_active', 'meta_title', 'meta_description'
        ]
        extra_kwargs = {
            'name': {'min_length': 1},
            'slug': {'min_length': 1},
            'description': {'min_length': 1},
            'base_price': {'required': True}
        }

class ProductResponseSerializer(BaseResponseSerializer):
    category = CategoryResponseSerializer(read_only=True)
    variants = ProductVariantResponseSerializer(many=True, read_only=True)
    images = ProductImageResponseSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'description',
            'base_price', 'is_active', 'variants', 'images',
            'main_image', 'meta_title', 'meta_description'
        ]
        read_only_fields = ['id']

    @extend_schema_field(ProductImageResponseSerializer)
    def get_main_image(self, obj) -> Optional[Dict[str, Any]]:
        main_image = obj.images.filter(type='main', is_active=True).first()
        if main_image:
            return ProductImageResponseSerializer(main_image).data
        return None

class ProductDetailResponseSerializer(ProductResponseSerializer):
    class Meta(ProductResponseSerializer.Meta):
        fields = ProductResponseSerializer.Meta.fields + ['created_at', 'updated_at']
        read_only_fields = ProductResponseSerializer.Meta.read_only_fields + ['created_at', 'updated_at']