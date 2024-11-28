from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from typing import List, Dict, Optional, Any

class BaseSerializer(serializers.ModelSerializer):
    """Base serializer with common functionality"""
    class Meta:
        abstract = True

class BaseRequestSerializer(BaseSerializer):
    """Base serializer for request validation"""
    class Meta:
        abstract = True

class BaseResponseSerializer(BaseSerializer):
    """Base serializer for response data"""
    class Meta:
        abstract = True