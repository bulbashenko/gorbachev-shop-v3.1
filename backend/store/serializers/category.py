from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from typing import List, Dict, Any
from .base import BaseRequestSerializer, BaseResponseSerializer
from ..models import Category

class CategoryRequestSerializer(BaseRequestSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'parent', 'is_active']
        extra_kwargs = {
            'name': {'min_length': 1},
            'slug': {'min_length': 1}
        }

class CategoryResponseSerializer(BaseResponseSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children', 'is_active']
        read_only_fields = ['id']

    @extend_schema_field(List[Dict])
    def get_children(self, obj) -> List[Dict[str, Any]]:
        """Get active child categories"""
        return CategoryResponseSerializer(
            obj.children.filter(is_active=True), 
            many=True
        ).data