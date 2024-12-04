from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Order, OrderStatus
from apps.notifications.services import EmailService

logger = logging.getLogger(__name__)

@receiver(post_save, sender=OrderStatus)
def handle_order_status_change(sender, instance, created, **kwargs):
    """Отправка уведомления при изменении статуса заказа"""
    try:
        logger.info(f"OrderStatus signal triggered. Status: {instance.status}, Order: {instance.order.order_number}")
        
        if created:
            # Получаем предыдущий статус
            previous_status = OrderStatus.objects.filter(
                order=instance.order
            ).exclude(
                id=instance.id
            ).order_by('-created_at').first()

            status_change = {
                'from': previous_status.status if previous_status else None,
                'to': instance.status,
                'notes': instance.notes
            }

            logger.info(f"Sending email notification for order {instance.order.order_number}")
            
            # Отправляем уведомление
            result = EmailService.send_order_status_update_email(
                instance.order,
                status_change
            )
            
            logger.info(f"Email notification result: {result}")

            # Обновляем временные метки на заказе
            order = instance.order
            if instance.status == Order.OrderStatus.SHIPPED:
                order.shipped_at = timezone.now()
            elif instance.status == Order.OrderStatus.DELIVERED:
                order.delivered_at = timezone.now()
            order.save()

    except Exception as e:
        logger.error(f"Error in order status signal: {str(e)}", exc_info=True)

# Добавим еще один сигнал для обновления основной модели Order
@receiver(post_save, sender=Order)
def handle_order_update(sender, instance, **kwargs):
    """Отправка уведомления при обновлении заказа"""
    try:
        logger.info(f"Order update signal triggered. Order: {instance.order_number}, Status: {instance.status}")
        
        # Создаем запись в истории статусов, если её еще нет
        if not OrderStatus.objects.filter(
            order=instance,
            status=instance.status
        ).exists():
            OrderStatus.objects.create(
                order=instance,
                status=instance.status,
                notes=f"Status updated to {instance.status}"
            )
            
        logger.info(f"Created OrderStatus record for {instance.order_number}")
            
    except Exception as e:
        logger.error(f"Error in order update signal: {str(e)}", exc_info=True)