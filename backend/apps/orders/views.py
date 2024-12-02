from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Order, OrderItem, OrderStatus
from apps.cart.models import Cart
from apps.payments.models import Payment
from apps.products.models import ProductVariant
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
    OrderTrackingSerializer
)

@extend_schema(tags=['orders'])
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для управления заказами"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__variant__product',
            'items__variant__size',
            'items__variant__color',
            'status_history'
        )

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
            cart = Cart.objects.select_for_update().get(user=request.user)
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Проверяем наличие товаров
            unavailable_items = []
            for item in cart.items.select_related('variant').all():
                if not item.is_available():
                    unavailable_items.append({
                        'product': item.variant.product.name,
                        'requested': item.quantity,
                        'available': item.variant.stock
                    })

            if unavailable_items:
                return Response(
                    {
                        'error': 'Some items are out of stock',
                        'items': unavailable_items
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = OrderCreateSerializer(data=request.data)
            if serializer.is_valid():
                # Генерируем номер заказа
                order_number = self._generate_order_number()

                # Расчет сумм с использованием Decimal
                subtotal = cart.get_total_price()
                shipping_cost = Decimal(str(self._calculate_shipping_cost(
                    serializer.validated_data['shipping_method']
                )))
                tax = Decimal('0.20') * subtotal  # 20% налог
                total = subtotal + shipping_cost + tax

                # Создаем заказ
                order = Order.objects.create(
                    order_number=order_number,
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
                    status=Order.OrderStatus.AWAITING_PAYMENT,
                    customer_notes=serializer.validated_data.get('customer_notes', '')
                )

                # Создаем элементы заказа и обновляем остатки
                order_items = []
                stock_updates = []
                
                for item in cart.items.all():
                    order_items.append(OrderItem(
                        order=order,
                        variant=item.variant,
                        quantity=item.quantity,
                        price=item.variant.product.current_price
                    ))
                    
                    variant = item.variant
                    variant.stock -= item.quantity
                    stock_updates.append(variant)

                # Пакетное создание элементов заказа
                OrderItem.objects.bulk_create(order_items)
                
                # Пакетное обновление остатков
                ProductVariant.objects.bulk_update(stock_updates, ['stock'])

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

                # Очищаем корзину и кеш
                cart.items.all().delete()
                cache.delete(f'cart_total_{cart.id}')

                # Инвалидируем кеш для аналитики
                cache.delete(f'daily_sales_{timezone.now().date()}')

                return Response({
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'payment_id': str(payment.id),
                    'status': 'Order created successfully'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _generate_order_number(self):
        """Генерация уникального номера заказа"""
        from datetime import datetime
        prefix = datetime.now().strftime('%y%m')
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by('order_number').last()
        
        if last_order:
            last_number = int(last_order.order_number[6:])
            new_number = last_number + 1
        else:
            new_number = 1
            
        return f"{prefix}{new_number:04d}"

    def _calculate_shipping_cost(self, shipping_method):
        """Расчет стоимости доставки"""
        costs = {
            Order.ShippingMethod.STANDARD: Decimal('10.00'),
            Order.ShippingMethod.EXPRESS: Decimal('20.00'),
            Order.ShippingMethod.PICKUP: Decimal('0.00')
        }
        return costs.get(shipping_method, Decimal('10.00'))

    @extend_schema(
        summary="Cancel order",
        description="Отмена заказа с возвратом товаров на склад",
        responses={
            200: {"type": "object", "properties": {"status": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in [Order.OrderStatus.AWAITING_PAYMENT, Order.OrderStatus.PROCESSING]:
            order.status = Order.OrderStatus.CANCELLED
            order.save()
            
            # Возвращаем товары в наличие
            stock_updates = []
            for item in order.items.select_related('variant').all():
                variant = item.variant
                variant.stock += item.quantity
                stock_updates.append(variant)
            
            # Пакетное обновление остатков
            ProductVariant.objects.bulk_update(stock_updates, ['stock'])

            # Добавляем запись в историю
            OrderStatus.objects.create(
                order=order,
                status=Order.OrderStatus.CANCELLED,
                notes='Order cancelled by customer',
                created_by=request.user
            )

            # Инвалидируем кеш для аналитики
            cache.delete(f'daily_sales_{timezone.now().date()}')

            return Response({'status': 'Order cancelled successfully'})
        return Response(
            {'error': 'Order cannot be cancelled in current status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Get order tracking",
        description="Получение информации о статусе заказа",
        responses={200: OrderTrackingSerializer}
    )
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        order = self.get_object()
        serializer = OrderTrackingSerializer(order)
        return Response(serializer.data)
