from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    """Отправка письма верификации при создании пользователя"""
    if created and not instance.email_verified:
        instance.send_verification_email()