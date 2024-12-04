from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Payment
from .serializers import PaymentSerializer
from .services import PaymentProcessor
import logging

logger = logging.getLogger('payment')

@extend_schema(tags=['payments'])
class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        """
        Оптимизированный QuerySet с предзагрузкой связанных данных
        """
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
            
        return Payment.objects.select_related(
            'order',
            'order__user',
            'order__shipping_address'
        ).prefetch_related(
            Prefetch(
                'order__items',
                queryset=self.order_items_queryset()
            )
        ).filter(
            order__user=self.request.user
        )
    
    def order_items_queryset(self):
        """
        Оптимизированный QuerySet для элементов заказа
        """
        from apps.orders.models import OrderItem
        return OrderItem.objects.select_related(
            'variant',
            'variant__product',
            'variant__size',
            'variant__color'
        )

    @extend_schema(
        summary="Process payment",
        description="Processes the payment for an order",
        responses={
            200: PaymentSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            403: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )


    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Обработка платежа с проверкой верификации email
        """
        # Проверка верификации email перед обработкой платежа
        if not request.user.email_verified:
            return Response(
                {
                    'error': 'Please verify your email before making a payment',
                    'verification_required': True
                },
                status=status.HTTP_403_FORBIDDEN
            )

        payment = self.get_object()
        logger.info(f"Starting payment processing for payment {payment.id}")
        
        try:
            if payment.status != 'pending':
                logger.warning(f"Attempted to process non-pending payment {payment.id}")
                return Response(
                    {'error': 'Payment already processed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Валидация входных данных
            payment_data = request.data
            if not self._validate_payment_data(payment_data):
                logger.error(f"Invalid payment data for payment {payment.id}")
                return Response(
                    {'error': 'Invalid payment data'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Обработка платежа
            processor = PaymentProcessor(payment.order, payment_data)
            processed_payment = processor.process_payment()
            
            logger.info(f"Payment {payment.id} processed successfully")
            return Response(
                PaymentSerializer(processed_payment).data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            logger.error(f"Validation error in payment {payment.id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in payment {payment.id}: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Refund payment",
        description="Processes a refund for a completed payment",
        responses={
            200: PaymentSerializer,
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """
        Обработка возврата платежа с логированием
        """
        payment = self.get_object()
        logger.info(f"Starting refund process for payment {payment.id}")
        
        try:
            if payment.status != 'completed':
                logger.warning(f"Attempted to refund non-completed payment {payment.id}")
                return Response(
                    {'error': 'Only completed payments can be refunded'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            processor = PaymentProcessor(payment.order, {})
            if processor.refund_payment(payment):
                logger.info(f"Payment {payment.id} refunded successfully")
                return Response(
                    PaymentSerializer(payment).data,
                    status=status.HTTP_200_OK
                )
            
            logger.error(f"Refund failed for payment {payment.id}")
            return Response(
                {'error': 'Refund processing failed'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in refund {payment.id}: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _validate_payment_data(self, data):
        """
        Валидация данных платежа
        """
        required_fields = ['method', 'card_number', 'expiry', 'cvv']
        return all(field in data for field in required_fields)

    @method_decorator(cache_page(60 * 15))  # Кеширование на 15 минут
    def list(self, request, *args, **kwargs):
        """
        Получение списка платежей с кешированием
        """
        return super().list(request, *args, **kwargs)
