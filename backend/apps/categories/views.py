from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Category
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryTreeSerializer
)

@extend_schema(tags=['categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления категориями товаров.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    @extend_schema(
        summary="Get category tree",
        description="Returns categories in a hierarchical tree structure",
        responses={200: CategoryTreeSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        # Get root categories (categories without parents)
        root_categories = Category.objects.filter(
            parent=None
        ).annotate(
            product_count=Count('products')
        )
        serializer = CategoryTreeSerializer(
            root_categories,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get menu categories",
        description="Returns active categories for navigation menu",
        responses={200: CategoryListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def menu(self, request):
        categories = Category.objects.filter(
            is_active=True,
            show_in_menu=True
        ).order_by('order')
        serializer = CategoryListSerializer(
            categories,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)