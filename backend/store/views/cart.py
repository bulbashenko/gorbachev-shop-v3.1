from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import logging

from ..models import Cart, CartItem
from ..serializers import (
    CartItemRequestSerializer,
    CartItemResponseSerializer,
    CartResponseSerializer,
)

logger = logging.getLogger(__name__)

class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.none()
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()

        return Cart.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related(
            'items__variant__product',
            'items__variant__images'
        )

    def get_object(self):
        """Get or create active cart for current user."""
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user,
            is_active=True,
            defaults={'total_amount': Decimal('0.00')}
        )
        return cart

    def get_serializer_class(self):
        return CartResponseSerializer

    def handle_exception(self, exc):
        """Convert Django ValidationError to DRF ValidationError."""
        if isinstance(exc, ValidationError):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request):
        """Get current user's active cart."""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        data = serializer.data
        # Ensure total_amount is formatted as string with 2 decimal places
        data['total_amount'] = '{:.2f}'.format(cart.total_amount)
        return Response(data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def add_item(self, request):
        """Add item to cart."""
        try:
            cart = self.get_object()
            serializer = CartItemRequestSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                variant_id = serializer.validated_data['variant_id']
                quantity = serializer.validated_data.get('quantity', 1)
                
                cart_item = cart.add_item(variant_id=variant_id, quantity=quantity)
                logger.info(f'Added item to cart: user={request.user.id}, variant={variant_id}')
                return Response(
                    CartItemResponseSerializer(cart_item).data, 
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(f'Error adding item to cart: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def update_item(self, request):
        """Update cart item quantity."""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            cart_item = cart.items.get(id=item_id)
            if quantity > 0:
                updated_item = cart.update_item(cart_item.variant, quantity)
                if updated_item:
                    return Response(CartItemResponseSerializer(updated_item).data)
                return Response(
                    {"detail": "Item removed from cart"},
                    status=status.HTTP_200_OK
                )
            else:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            logger.error(f'Error updating cart item: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def clear(self, request):
        """Remove all items from cart."""
        cart = self.get_object()
        cart.clear()
        logger.info(f'Cleared cart: user={request.user.id}')
        return Response(status=status.HTTP_204_NO_CONTENT)