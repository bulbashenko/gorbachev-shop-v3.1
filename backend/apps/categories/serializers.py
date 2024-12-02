from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from typing import Dict, List
from .models import Category

class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer for basic category information"""
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'is_active')

class CategorySerializer(serializers.ModelSerializer):
    """Full category serializer with nested children"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description',
            'parent', 'children', 'image', 'icon',
            'is_active', 'show_in_menu', 'order',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

    @extend_schema_field({'type': 'array', 'items': {'$ref': '#/components/schemas/Category'}})
    def get_children(self, obj) -> List[Dict]:
        children = obj.get_children()
        return CategorySerializer(children, many=True, context=self.context).data

class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive category serializer for tree structure"""
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children', 'product_count')

    @extend_schema_field({'type': 'array', 'items': {'$ref': '#/components/schemas/CategoryTree'}})
    def get_children(self, obj) -> List[Dict]:
        children = obj.get_children()
        return CategoryTreeSerializer(children, many=True, context=self.context).data

    @extend_schema_field(serializers.IntegerField())
    def get_product_count(self, obj) -> int:
        return obj.products.count()