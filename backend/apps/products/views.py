from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Prefetch, Count
from django.core.cache import cache
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Product, ProductVariant, ProductImage, Size, Color
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductVariantSerializer,
    SizeSerializer,
    ColorSerializer
)
from .filters import ProductFilter

@extend_schema(tags=['products'])
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для управления товарами"""
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()

        # Базовый queryset с оптимизированными запросами
        queryset = Product.objects.filter(
            is_active=True
        ).select_related(
            'category'
        ).prefetch_related(
            Prefetch(
                'variants',
                queryset=ProductVariant.objects.select_related('size', 'color')
            ),
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_main=True)
            )
        )

        # Фильтрация по наличию
        in_stock = self.request.query_params.get('in_stock')
        if in_stock:
            queryset = queryset.filter(variants__stock__gt=0).distinct()

        # Фильтрация по цене
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_object(self):
        """
        Получение объекта с использованием кеширования
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        # Пытаемся получить из кеша
        cache_key = f'product_{lookup_value}'
        product = cache.get(cache_key)

        if not product:
            product = super().get_object()
            # Кешируем на 1 час
            cache.set(cache_key, product, 3600)

        return product

    def list(self, request, *args, **kwargs):
        """
        Получение списка товаров с кешированием
        """
        # Формируем ключ кеша на основе параметров запроса
        cache_key = f'products_list_{request.query_params.urlencode()}'
        response_data = cache.get(cache_key)

        if not response_data:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data = self.get_paginated_response(serializer.data).data
            else:
                serializer = self.get_serializer(queryset, many=True)
                response_data = serializer.data

            # Кешируем на 15 минут
            cache.set(cache_key, response_data, 900)

        return Response(response_data)

    @extend_schema(
        summary="Get product variants",
        description="Получение вариантов товара",
        responses={200: ProductVariantSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """
        Получение вариантов товара с фильтрацией по размеру и цвету
        """
        product = self.get_object()
        
        # Фильтрация по размеру и цвету
        size = request.query_params.get('size')
        color = request.query_params.get('color')
        in_stock = request.query_params.get('in_stock')

        variants = product.variants.select_related('size', 'color')

        if size:
            variants = variants.filter(size__name=size)
        if color:
            variants = variants.filter(color__name=color)
        if in_stock:
            variants = variants.filter(stock__gt=0)

        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get available sizes",
        description="Получение доступных размеров товара",
        responses={200: SizeSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def sizes(self, request, pk=None):
        """
        Получение доступных размеров товара
        """
        product = self.get_object()
        color = request.query_params.get('color')
        in_stock = request.query_params.get('in_stock')

        sizes = Size.objects.filter(
            productvariant__product=product
        )

        if color:
            sizes = sizes.filter(productvariant__color__name=color)
        if in_stock:
            sizes = sizes.filter(productvariant__stock__gt=0)

        sizes = sizes.distinct()
        serializer = SizeSerializer(sizes, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get available colors",
        description="Получение доступных цветов товара",
        responses={200: ColorSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def colors(self, request, pk=None):
        """
        Получение доступных цветов товара
        """
        product = self.get_object()
        size = request.query_params.get('size')
        in_stock = request.query_params.get('in_stock')

        colors = Color.objects.filter(
            productvariant__product=product
        )

        if size:
            colors = colors.filter(productvariant__size__name=size)
        if in_stock:
            colors = colors.filter(productvariant__stock__gt=0)

        colors = colors.distinct()
        serializer = ColorSerializer(colors, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Check stock",
        description="Проверка наличия товара",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "in_stock": {"type": "boolean"},
                    "available_quantity": {"type": "integer"}
                }
            }
        }
    )
    @action(detail=True, methods=['get'])
    def check_stock(self, request, pk=None):
        """
        Проверка наличия товара с указанными параметрами
        """
        product = self.get_object()
        size = request.query_params.get('size')
        color = request.query_params.get('color')

        try:
            variant = product.variants.get(
                size__name=size,
                color__name=color
            )
            return Response({
                'in_stock': variant.stock > 0,
                'available_quantity': variant.stock
            })
        except ProductVariant.DoesNotExist:
            return Response({
                'in_stock': False,
                'available_quantity': 0
            })

    @extend_schema(
        summary="Similar products",
        description="Получение похожих товаров",
        responses={200: ProductListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """
        Получение похожих товаров на основе категории и характеристик
        """
        product = self.get_object()
        cache_key = f'similar_products_{product.id}'
        similar_products = cache.get(cache_key)

        if not similar_products:
            # Находим похожие товары
            similar_products = Product.objects.filter(
                Q(category=product.category) |
                Q(brand=product.brand)
            ).exclude(
                id=product.id
            ).filter(
                is_active=True
            ).distinct()[:5]

            # Кешируем на 1 час
            cache.set(cache_key, similar_products, 3600)

        serializer = ProductListSerializer(similar_products, many=True)
        return Response(serializer.data)
