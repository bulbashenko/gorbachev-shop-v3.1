from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.products.models import ProductVariant

@extend_schema(tags=['cart'])
class CartViewSet(viewsets.ModelViewSet):
    """ViewSet для управления корзиной покупок"""
    serializer_class = CartSerializer
    queryset = Cart.objects.none()
    
    def get_permissions(self):
        """
        Разрешаем анонимный доступ для гостевых корзин,
        но требуем аутентификацию для некоторых действий
        """
        if self.action in ['checkout', 'transfer_to_user']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.filter(id=self.request.cart.id).prefetch_related(
            'items__variant__product',
            'items__variant__size',
            'items__variant__color'
        )

    @extend_schema(
        summary="Add item to cart",
        description="Добавляет товар в корзину с проверкой наличия",
        request=CartItemSerializer,
        responses={
            201: CartItemSerializer,
            400: OpenApiResponse(description="Invalid input or out of stock"),
            404: OpenApiResponse(description="Product variant not found"),
        }
    )
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def add_item(self, request):
        cart = request.cart
        serializer = CartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            variant_id = serializer.validated_data['variant'].id
            quantity = serializer.validated_data['quantity']
            
            # Проверяем наличие с использованием кеша
            cache_key = f'variant_stock_{variant_id}'
            stock = cache.get(cache_key)
            
            if stock is None:
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    stock = variant.stock
                    cache.set(cache_key, stock, 300)  # кешируем на 5 минут
                except ProductVariant.DoesNotExist:
                    return Response(
                        {'error': 'Product variant not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Проверяем текущее количество в корзине
            current_item = cart.items.filter(variant_id=variant_id).first()
            current_quantity = current_item.quantity if current_item else 0
            
            # Проверяем доступность с учетом текущего количества
            if stock < (current_quantity + quantity):
                return Response(
                    {
                        'error': 'Not enough stock',
                        'available': stock - current_quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Добавляем или обновляем товар в корзине
            if current_item:
                current_item.quantity += quantity
                current_item.save()
                serializer = CartItemSerializer(current_item)
            else:
                serializer.save(cart=cart)
            
            # Обновляем общую сумму корзины в кеше
            cache.delete(f'cart_total_{cart.id}')
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Remove item from cart",
        description="Удаляет товар из корзины",
        responses={204: None}
    )
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        try:
            item = CartItem.objects.get(pk=pk, cart=request.cart)
            item.delete()
            # Обновляем общую сумму корзины в кеше
            cache.delete(f'cart_total_{request.cart.id}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update item quantity",
        description="Обновляет количество товара в корзине с проверкой наличия",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'quantity': {'type': 'integer', 'minimum': 1}
                },
                'required': ['quantity']
            }
        },
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Invalid quantity or out of stock"),
            404: OpenApiResponse(description="Item not found")
        }
    )
    @action(detail=True, methods=['patch'])
    @transaction.atomic
    def update_quantity(self, request, pk=None):
        try:
            item = CartItem.objects.get(pk=pk, cart=request.cart)
            quantity = request.data.get('quantity', 1)
            
            if quantity <= 0:
                return Response(
                    {'error': 'Quantity must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверяем наличие с использованием кеша
            cache_key = f'variant_stock_{item.variant.id}'
            stock = cache.get(cache_key)
            
            if stock is None:
                stock = item.variant.stock
                cache.set(cache_key, stock, 300)  # кешируем на 5 минут
            
            if stock < quantity:
                return Response(
                    {
                        'error': 'Not enough stock',
                        'available': stock
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.quantity = quantity
            item.save()
            
            # Обновляем общую сумму корзины в кеше
            cache.delete(f'cart_total_{request.cart.id}')
            
            serializer = CartItemSerializer(item)
            return Response(serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Validate cart",
        description="Проверяет наличие всех товаров в корзине",
        responses={
            200: OpenApiResponse(description="Cart is valid"),
            400: OpenApiResponse(description="Cart validation failed")
        }
    )
    @action(detail=False, methods=['get'])
    def validate(self, request):
        cart = request.cart
        invalid_items = []
        
        for item in cart.items.all():
            if not item.is_available():
                invalid_items.append({
                    'id': str(item.id),
                    'product': item.variant.product.name,
                    'variant': str(item.variant),
                    'requested': item.quantity,
                    'available': item.variant.stock
                })
        
        if invalid_items:
            return Response(
                {
                    'error': 'Some items are out of stock',
                    'invalid_items': invalid_items
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({'status': 'Cart is valid'})

    @extend_schema(
        summary="Clear cart",
        description="Очищает корзину",
        responses={204: None}
    )
    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = request.cart
        cart.items.all().delete()
        # Обновляем общую сумму корзины в кеше
        cache.delete(f'cart_total_{cart.id}')
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Transfer guest cart",
        description="Переносит гостевую корзину к пользователю",
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description="Transfer failed")
        }
    )
    @action(detail=False, methods=['post'])
    def transfer_to_user(self, request):
        cart = request.cart
        if cart.session_id and request.user.is_authenticated:
            cart.transfer_to_user(request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        return Response(
            {'error': 'Invalid cart transfer request'},
            status=status.HTTP_400_BAD_REQUEST
        )
