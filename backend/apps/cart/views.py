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

    def list(self, request, *args, **kwargs):
        """Get current cart with items"""
        cart = request.cart
        print(f"Cart list: cart_id={cart.id}, items_count={cart.items.count()}")  # Debug log
        serializer = self.get_serializer(cart)
        data = serializer.data
        print(f"Serialized cart data: {data}")  # Debug log
        return Response(data)

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
            variant_id = serializer.validated_data.get('variant_id')
            quantity = serializer.validated_data.get('quantity', 1)
            
            try:
                variant = ProductVariant.objects.get(id=variant_id)
            except ProductVariant.DoesNotExist:
                return Response(
                    {'error': 'Product variant not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Проверка наличия на складе
            if variant.stock < quantity:
                return Response(
                    {
                        'error': 'Not enough stock',
                        'available': variant.stock
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Добавляем или обновляем товар в корзине
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Если товар уже есть в корзине, обновляем количество
                cart_item.quantity += quantity
                if cart_item.quantity > variant.stock:
                    return Response(
                        {
                            'error': 'Not enough stock',
                            'available': variant.stock
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Remove item from cart",
        description="Удаляет товар из корзины",
        responses={204: None}
    )
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        try:
            item_id = request.data.get('item_id')
            if not item_id:
                return Response(
                    {'error': 'Item ID is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            item = CartItem.objects.get(id=item_id, cart=request.cart)
            item.delete()
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
    @action(detail=False, methods=['patch'])
    def update_quantity(self, request):
        try:
            item_id = request.data.get('item_id')
            quantity = request.data.get('quantity')
            
            print(f"Updating quantity: item_id={item_id}, quantity={quantity}")  # Debug log
            
            if not item_id or quantity is None:
                return Response(
                    {'error': 'Item ID and quantity are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart = request.cart
            item = cart.items.get(id=item_id)
            
            # Проверяем наличие на складе
            if item.variant.stock < quantity:
                return Response(
                    {'error': f'Only {item.variant.stock} items available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            item.quantity = quantity
            item.save()
            
            # Возвращаем обновленную корзину
            cart_serializer = self.get_serializer(cart)
            return Response(cart_serializer.data)
            
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

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
        if not request.user.is_authenticated:
            return Response(
                {'error': 'User must be authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if not cart.session_id:
            return Response({'message': 'No guest cart to transfer'})

        cart.transfer_to_user(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

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