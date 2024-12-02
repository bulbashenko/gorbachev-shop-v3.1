from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Min, Max
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Product, ProductVariant, Size, Color
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductVariantSerializer
)
from .filters import ProductFilter

@extend_schema(tags=['products'])
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для управления товарами.
    Предоставляет только операции чтения.
    """
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand']
    ordering_fields = [
        'name', 'price', 'created_at',
        'sale_price'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            'variants',
            'variants__size',
            'variants__color',
            'images'
        )
        return queryset

    @extend_schema(
        summary="Get available filters",
        description="Returns available filter options with counts and price ranges",
        responses={200: {
            "type": "object",
            "properties": {
                "price_range": {
                    "type": "object",
                    "properties": {
                        "min_price": {"type": "number"},
                        "max_price": {"type": "number"}
                    }
                },
                "sizes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "count": {"type": "integer"}
                        }
                    }
                },
                "colors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "code": {"type": "string"},
                            "count": {"type": "integer"}
                        }
                    }
                },
                "brands": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "brand": {"type": "string"},
                            "count": {"type": "integer"}
                        }
                    }
                },
                "on_sale_count": {"type": "integer"},
                "in_stock_count": {"type": "integer"}
            }
        }}
    )
    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Получение доступных фильтров с количеством товаров"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get price range
        price_range = queryset.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )

        # Get available sizes with count
        sizes = Size.objects.filter(
            productvariant__product__in=queryset
        ).annotate(
            count=Count('productvariant__product', distinct=True)
        ).values('id', 'name', 'count')

        # Get available colors with count
        colors = Color.objects.filter(
            productvariant__product__in=queryset
        ).annotate(
            count=Count('productvariant__product', distinct=True)
        ).values('id', 'name', 'code', 'count')

        # Get brands with count
        brands = queryset.values('brand').annotate(
            count=Count('id')
        )

        # Count on sale items
        on_sale_count = queryset.filter(
            sale_price__isnull=False
        ).count()

        # Count in stock items
        in_stock_count = queryset.filter(
            variants__stock__gt=0
        ).distinct().count()

        return Response({
            'price_range': price_range,
            'sizes': sizes,
            'colors': colors,
            'brands': brands,
            'on_sale_count': on_sale_count,
            'in_stock_count': in_stock_count
        })

    @extend_schema(
        summary="Get product variants",
        description="Returns available variants for the product",
        responses={200: ProductVariantSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Получение доступных вариантов товара"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Check variant availability",
        description="Checks if specific variant is available",
        parameters=[
            OpenApiParameter(
                name="size",
                description="Size ID",
                required=True,
                type=int
            ),
            OpenApiParameter(
                name="color",
                description="Color ID",
                required=True,
                type=int
            )
        ],
        responses={200: {
            "type": "object",
            "properties": {
                "available": {"type": "boolean"},
                "stock": {"type": "integer"}
            }
        }}
    )
    @action(detail=True, methods=['get'])
    def check_availability(self, request, pk=None):
        """Проверка наличия конкретного варианта"""
        product = self.get_object()
        size_id = request.query_params.get('size')
        color_id = request.query_params.get('color')
        
        try:
            variant = product.variants.get(
                size_id=size_id,
                color_id=color_id
            )
            return Response({
                'available': variant.stock > 0,
                'stock': variant.stock
            })
        except ProductVariant.DoesNotExist:
            return Response({
                'available': False,
                'stock': 0
            })