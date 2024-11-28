from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin
)
from django.core.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.utils import extend_schema
import logging

from ..models import Order, Cart
from ..serializers import (
    CreateOrderRequestSerializer,
    UpdateOrderRequestSerializer,
    OrderResponseSerializer,
)

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.GenericViewSet,
                  CreateModelMixin,
                  RetrieveModelMixin,
                  UpdateModelMixin,
                  ListModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.none()
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        queryset = Order.objects.prefetch_related(
            'items__variant__product',
            'items__variant__images'
        ).select_related('user').order_by('-created_at')

        # Admin users can see all orders
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderRequestSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateOrderRequestSerializer
        return OrderResponseSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new order from the user's active cart."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get active cart
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if not cart or not cart.items.exists():
                raise ValidationError(_("No active cart found or cart is empty"))

            # Create order
            order = Order.objects.create(
                user=request.user,
                status='pending',
                shipping_address=serializer.validated_data['shipping_address'],
                shipping_method=serializer.validated_data['shipping_method'],
                notes=serializer.validated_data.get('notes', ''),
                total_amount=cart.total_amount
            )
            
            # Create order items and process cart
            order.create_from_cart(cart)
            
            # Return response
            logger.info(f'Created order: user={request.user.id}, order={order.id}')
            response_serializer = OrderResponseSerializer(order)
            headers = self.get_success_headers(serializer.data)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            logger.error(f'Error creating order: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @transaction.atomic
    def perform_update(self, serializer):
        """Update order with validation."""
        try:
            order = serializer.save()
            logger.info(f'Updated order: {order.id}')
            return order
        except ValidationError as e:
            logger.error(f'Error updating order: {str(e)}')
            raise DRFValidationError(detail=str(e))

    @action(detail=True, methods=['post'])
    @extend_schema(
        description="Cancel order",
        request=None,
        responses={200: OrderResponseSerializer}
    )
    @transaction.atomic
    def cancel(self, request, pk=None):
        """Cancel an order and return items to stock."""
        order = self.get_object()
        try:
            # Only order owner or admin can cancel
            if not request.user.is_staff and order.user != request.user:
                return Response(
                    {'error': 'Not authorized to cancel this order'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            order.cancel()
            logger.info(f'Cancelled order: user={request.user.id}, order={order.id}')
            serializer = self.get_serializer(order)
            return Response(serializer.data)
            
        except ValidationError as e:
            logger.error(f'Error cancelling order: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )