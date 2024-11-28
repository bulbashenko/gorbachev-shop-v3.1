from rest_framework import viewsets, serializers, filters
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from django.core.exceptions import ValidationError
from django.db.models import Q, Prefetch, Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
import logging

from ..models import Category, Product
from ..serializers import (
    CategoryRequestSerializer, 
    CategoryResponseSerializer, 
    ProductResponseSerializer
)

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(
        description="Get list of categories",
        responses=inline_serializer(
            name='PaginatedCategoryResponse',
            fields={
                'count': serializers.IntegerField(),
                'next': serializers.URLField(allow_null=True),
                'previous': serializers.URLField(allow_null=True),
                'results': CategoryResponseSerializer(many=True),
            }
        )
    ),
    retrieve=extend_schema(
        description="Get category details",
        responses=CategoryResponseSerializer
    )
)
class CategoryViewSet(viewsets.GenericViewSet,
                     ListModelMixin,
                     RetrieveModelMixin):
    """
    ViewSet for Category model providing list and retrieve operations.
    Includes caching, filtering, and extended product information.
    """
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        """
        Override to ensure only admin users can create/update categories.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        """
        Get the list of categories with optimized queries and filtering.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()

        # Base queryset with active categories
        queryset = Category.objects.filter(is_active=True)

        # Include product counts and active products
        queryset = queryset.annotate(
            total_products=Count('products', filter=Q(products__is_active=True)),
            active_variants=Count(
                'products__variants',
                filter=Q(
                    products__is_active=True,
                    products__variants__is_active=True,
                    products__variants__stock_quantity__gt=0
                )
            )
        )

        # Add prefetch related for products if needed
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                Prefetch(
                    'products',
                    queryset=Product.objects.filter(is_active=True).select_related('category')
                ),
                'children'
            )

        # Handle search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(slug__icontains=search) |
                Q(description__icontains=search)
            )

        # Filter by parent category
        parent = self.request.query_params.get('parent')
        if parent == 'null':
            queryset = queryset.filter(parent__isnull=True)
        elif parent:
            queryset = queryset.filter(parent__slug=parent)

        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryRequestSerializer
        return CategoryResponseSerializer

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """
        Get list of categories with caching.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Get detailed category information including products.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Add additional product information if requested
        if request.query_params.get('include_products') == 'true':
            products = instance.products.filter(is_active=True)
            data['products'] = ProductResponseSerializer(products, many=True).data

        return Response(data)

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create a new category with validation.
        """
        try:
            category = serializer.save()
            logger.info(f'Created category: {category.name} (slug: {category.slug})')
        except ValidationError as e:
            logger.error(f'Error creating category: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Update category with validation.
        """
        try:
            category = serializer.save()
            logger.info(f'Updated category: {category.name} (slug: {category.slug})')
        except ValidationError as e:
            logger.error(f'Error updating category: {str(e)}')
            raise DRFValidationError(detail=str(e))

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete category by setting is_active to False.
        """
        instance = self.get_object()
        
        # Check if category has active products
        if instance.products.filter(is_active=True).exists():
            return Response(
                {'error': 'Cannot delete category with active products'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.is_active = False
        instance.save()
        logger.info(f'Deactivated category: {instance.name} (slug: {instance.slug})')
        
        return Response(status=status.HTTP_204_NO_CONTENT)