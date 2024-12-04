from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderStatus
from apps.notifications.services import EmailService

@receiver(post_save, sender=OrderStatus)
def send_order_status_notification(sender, instance, created, **kwargs):
    """Отправка уведомления при изменении статуса заказа"""
    if created:
        # Получаем предыдущий статус
        previous_status = OrderStatus.objects.filter(
            order=instance.order
        ).exclude(
            id=instance.id
        ).order_by('-created_at').first()

        # Отправляем уведомление
        EmailService.send_order_notification(
            instance.order,
            {
                'from': previous_status.status if previous_status else None,
                'to': instance.status,
                'notes': instance.notes
            }
        )