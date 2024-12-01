from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiExample
from typing import Dict, List, Optional
from .models import Product, ProductVariant, ProductImage, Size, Color

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'code']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'color', 'is_main', 'order']

class ProductVariantSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    available = serializers.BooleanField(source='stock_available')
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'sku', 'stock', 'available']

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name',
            'brand', 'price', 'sale_price',
            'main_image', 'discount_percent',
            'available_sizes', 'available_colors'
        ]

    @extend_schema_field(serializers.URLField())
    def get_main_image(self, obj) -> Optional[str]:
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return self.context['request'].build_absolute_uri(main_image.image.url)
        return None

    @extend_schema_field(serializers.FloatField())
    def get_discount_percent(self, obj) -> Optional[float]:
        if obj.sale_price and obj.price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 2)
        return None

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_available_sizes(self, obj) -> List[str]:
        return list(obj.get_available_sizes().values_list('name', flat=True))

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_available_colors(self, obj) -> List[str]:
        return list(obj.get_available_colors().values_list('name', flat=True))

class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    available_sizes = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'category', 'category_name', 'brand', 'gender',
            'price', 'sale_price', 'discount_percent',
            'material', 'care_instructions',
            'main_image', 'images', 'variants',
            'available_sizes', 'available_colors',
            'related_products', 'created_at'
        ]

    @extend_schema_field(serializers.URLField())
    def get_main_image(self, obj) -> Optional[str]:
        main_image = obj.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return self.context['request'].build_absolute_uri(main_image.image.url)
        return None

    @extend_schema_field(SizeSerializer(many=True))
    def get_available_sizes(self, obj) -> List[Dict]:
        sizes = obj.get_available_sizes()
        return SizeSerializer(sizes, many=True).data

    @extend_schema_field(ColorSerializer(many=True))
    def get_available_colors(self, obj) -> List[Dict]:
        colors = obj.get_available_colors()
        return ColorSerializer(colors, many=True).data

    @extend_schema_field(serializers.FloatField())
    def get_discount_percent(self, obj) -> Optional[float]:
        if obj.sale_price and obj.price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 2)
        return None

    @extend_schema_field(ProductListSerializer(many=True))
    def get_related_products(self, obj) -> List[Dict]:
        related = Product.objects.filter(
            category=obj.category,
            gender=obj.gender
        ).exclude(id=obj.id)[:4]
        return ProductListSerializer(
            related,
            many=True,
            context=self.context
        ).data