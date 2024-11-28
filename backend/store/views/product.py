from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
import logging

from ..models import Product, ProductVariant, ProductImage
from ..serializers import (
    ProductRequestSerializer,
    ProductResponseSerializer,
    ProductDetailResponseSerializer,
    ProductImageRequestSerializer,
    ProductImageResponseSerializer,
    ProductVariantRequestSerializer,
    ProductVariantResponseSerializer,
)

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.GenericViewSet,
                    CreateModelMixin,
                    RetrieveModelMixin,
                    UpdateModelMixin,
                    DestroyModelMixin,
                    ListModelMixin):
    """
    ViewSet for Product model providing full CRUD operations.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'variants__sku']
    ordering_fields = ['name', 'created_at', 'base_price']
    ordering = ['-created_at']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions based on action.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        """
        Get the list of items for this view.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()

        queryset = Product.objects.select_related('category')
        
        if self.action in ['retrieve', 'update']:
            queryset = queryset.prefetch_related(
                Prefetch('variants', queryset=ProductVariant.objects.filter(is_active=True)),
                Prefetch('images', queryset=ProductImage.objects.filter(is_active=True).order_by('order')),
            )
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
            
        return queryset

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ProductRequestSerializer
        if self.action == 'retrieve':
            return ProductDetailResponseSerializer
        return ProductResponseSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create a new product with validation.
        """
        try:
            product = serializer.save()
            logger.info(f'Created product: {product.name} (slug: {product.slug})')
            
            # Create default variant if none provided
            if not product.variants.exists():
                default_variant = ProductVariant.objects.create(
                    product=product,
                    sku=f"{product.slug}-default",
                    attributes={},
                    stock_quantity=0
                )
                logger.info(f'Created default variant for product: {product.slug} (SKU: {default_variant.sku})')
                
        except ValidationError as e:
            logger.error(f'Error creating product: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Update product with validation.
        """
        try:
            product = serializer.save()
            logger.info(f'Updated product: {product.name} (slug: {product.slug})')
            return product
        except ValidationError as e:
            logger.error(f'Error updating product: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def add_variant(self, request, slug=None):
        """
        Add a new variant to the product.
        """
        product = self.get_object()
        serializer = ProductVariantRequestSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                variant = serializer.save(product=product)
                logger.info(f'Added variant to product {product.name} (SKU: {variant.sku})')
                return Response(
                    ProductVariantResponseSerializer(variant).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(f'Error adding variant: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def upload_images(self, request, slug=None):
        """
        Upload images for the product.
        """
        product = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_data = []
        errors = []
        
        for image in images:
            serializer = ProductImageRequestSerializer(data={
                'image': image,
                'alt_text': request.data.get('alt_text', product.name),
                'type': request.data.get('type', 'gallery')
            })
            
            try:
                if serializer.is_valid():
                    image_obj = serializer.save(product=product)
                    response_serializer = ProductImageResponseSerializer(image_obj)
                    image_data.append(response_serializer.data)
                    logger.info(f'Added image to product {product.name} (type: {image_obj.type})')
                else:
                    errors.append(serializer.errors)
            except ValidationError as e:
                errors.append(str(e))
                logger.error(f'Error uploading image: {str(e)}')

        if errors and not image_data:
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            {
                'images': image_data,
                'errors': errors if errors else None
            },
            status=status.HTTP_201_CREATED if image_data else status.HTTP_400_BAD_REQUEST
        )


class ProductVariantViewSet(viewsets.GenericViewSet,
                          CreateModelMixin,
                          RetrieveModelMixin,
                          UpdateModelMixin,
                          DestroyModelMixin,
                          ListModelMixin):
    """
    ViewSet for ProductVariant model providing CRUD operations.
    """
    queryset = ProductVariant.objects.select_related('product').filter(is_active=True)
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product', 'is_active']
    search_fields = ['sku', 'product__name']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductVariantRequestSerializer
        return ProductVariantResponseSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        try:
            variant = serializer.save()
            logger.info(f'Created variant: {variant.sku}')
        except ValidationError as e:
            logger.error(f'Error creating variant: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @transaction.atomic
    def perform_update(self, serializer):
        try:
            old_obj = self.get_object()
            variant = serializer.save()
            
            # Log stock changes
            if old_obj.stock_quantity != variant.stock_quantity:
                logger.info(
                    f'Stock updated for variant {variant.sku}: '
                    f'{old_obj.stock_quantity} -> {variant.stock_quantity}'
                )
            return variant
        except ValidationError as e:
            logger.error(f'Error updating variant: {str(e)}')
            raise DRFValidationError(detail=str(e))

    def perform_destroy(self, instance):
        """
        Soft delete the variant.
        """
        instance.is_active = False
        instance.save()
        logger.info(f'Deactivated variant: {instance.sku}')