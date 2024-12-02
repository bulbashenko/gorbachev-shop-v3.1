from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

@extend_schema(tags=['cart'])
class CartViewSet(viewsets.ModelViewSet):
    """ViewSet для управления корзиной покупок"""
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.none()  # Default empty queryset for schema generation
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Add item to cart",
        description="Добавляет товар в корзину",
        request=CartItemSerializer,
        responses={
            201: CartItemSerializer,
            400: OpenApiResponse(description="Invalid input"),
        }
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = request.cart
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cart=cart)
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
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update item quantity",
        description="Обновляет количество товара в корзине",
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
            400: OpenApiResponse(description="Invalid quantity"),
            404: OpenApiResponse(description="Item not found")
        }
    )
    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        try:
            item = CartItem.objects.get(pk=pk, cart=request.cart)
            quantity = request.data.get('quantity', 1)
            if quantity > 0:
                item.quantity = quantity
                item.save()
                serializer = CartItemSerializer(item)
                return Response(serializer.data)
            return Response(
                {'error': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)