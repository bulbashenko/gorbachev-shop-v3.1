from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Order, OrderItem, OrderStatus
from apps.cart.models import Cart
from apps.payments.models import Payment
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
    OrderTrackingSerializer
)

@extend_schema(tags=['orders'])
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заказами.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.none()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Create order from cart",
        description="Creates a new order from the current user's cart",
        request=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            403: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def create_from_cart(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = OrderCreateSerializer(data=request.data)
            if serializer.is_valid():
                # Расчет сумм с использованием Decimal
                subtotal = cart.get_total_price()
                shipping_cost = Decimal(str(self._calculate_shipping_cost(
                    serializer.validated_data['shipping_method']
                )))
                tax = Decimal('0.20') * subtotal  # 20% налог
                total = subtotal + shipping_cost + tax

                # Создаем заказ
                order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    phone=request.user.phone,
                    shipping_address=serializer.validated_data['shipping_address'],
                    billing_address=serializer.validated_data.get('billing_address'),
                    shipping_method=serializer.validated_data['shipping_method'],
                    shipping_cost=shipping_cost,
                    subtotal=subtotal,
                    tax=tax,
                    total=total,
                    status=Order.OrderStatus.AWAITING_PAYMENT
                )

                # Создаем элементы заказа
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        quantity=item.quantity,
                        price=Decimal(str(item.variant.product.current_price))
                    )
                    item.variant.stock -= item.quantity
                    item.variant.save()

                # Создаем запись в истории статусов
                OrderStatus.objects.create(
                    order=order,
                    status=Order.OrderStatus.AWAITING_PAYMENT,
                    notes='Order created',
                    created_by=request.user
                )

                # Создаем платеж
                payment = Payment.objects.create(
                    order=order,
                    amount=total,
                    payment_method=serializer.validated_data['payment_method'],
                    status=Payment.PaymentStatus.PENDING
                )

                # Очищаем корзину
                cart.items.all().delete()

                return Response({
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'payment_id': payment.id,
                    'status': 'Order created successfully'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _calculate_shipping_cost(self, shipping_method):
        """Расчет стоимости доставки"""
        costs = {
            Order.ShippingMethod.STANDARD: Decimal('10.00'),
            Order.ShippingMethod.EXPRESS: Decimal('20.00'),
            Order.ShippingMethod.PICKUP: Decimal('0.00')
        }
        return costs.get(shipping_method, Decimal('10.00'))

    def _calculate_tax(self, subtotal):
        """Расчет налога"""
        return subtotal * 0.20  # 20% налог

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in [Order.OrderStatus.AWAITING_PAYMENT, Order.OrderStatus.PROCESSING]:  # Fixed: Using proper status enum
            order.status = Order.OrderStatus.CANCELLED
            order.save()
            
            # Возвращаем товары в наличие
            for item in order.items.all():
                variant = item.variant
                variant.stock += item.quantity
                variant.save()

            # Добавляем запись в историю
            OrderStatus.objects.create(
                order=order,
                status=Order.OrderStatus.CANCELLED,
                notes='Order cancelled by customer',
                created_by=request.user
            )

            return Response({'status': 'Order cancelled successfully'})
        return Response(
            {'error': 'Order cannot be cancelled in current status'},
            status=status.HTTP_400_BAD_REQUEST
        )