from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import logging
from .models import EmailTemplate, EmailLog
from .utils import run_async

logger = logging.getLogger('notifications')

class EmailService:
    @classmethod
    @run_async
    def _send_email_async(cls, template_name: str, recipient_email: str, context: dict = None, user=None):
        """Асинхронная отправка email"""
        try:
            template = EmailTemplate.objects.get(name=template_name)
            context = context or {}
            
            # Создаем лог
            with transaction.atomic():
                email_log = EmailLog.objects.create(
                    template=template,
                    recipient=user,
                    recipient_email=recipient_email,
                    subject=Template(template.subject).render(Context(context)),
                    context=context
                )
            
                try:
                    # Рендерим контент
                    html_content = Template(template.html_content).render(Context(context))
                    text_content = Template(template.text_content).render(Context(context))
                    
                    # Отправляем email
                    send_mail(
                        subject=email_log.subject,
                        message=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient_email],
                        html_message=html_content,
                        fail_silently=False
                    )
                    
                    # Обновляем лог
                    email_log.status = EmailLog.Status.SENT
                    email_log.sent_at = timezone.now()
                    email_log.save()
                    
                    logger.info(f"Email sent successfully to {recipient_email}")
                    return True
                    
                except Exception as e:
                    email_log.status = EmailLog.Status.FAILED
                    email_log.error_message = str(e)
                    email_log.save()
                    logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
                    return False
                
        except EmailTemplate.DoesNotExist:
            logger.error(f"Email template '{template_name}' not found")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False

    @classmethod
    def send_email(cls, template_name: str, recipient_email: str, context: dict = None, user=None):
        """Запуск асинхронной отправки email"""
        cls._send_email_async(template_name, recipient_email, context, user)
        return True

    @classmethod
    def send_verification_email(cls, user):
        """Отправка письма верификации"""
        from django.contrib.auth.tokens import default_token_generator
        
        try:
            token = default_token_generator.make_token(user)
            verify_url = f"{settings.SITE_URL}/api/users/auth/verify-email/?token={token}"
            
            # Обновляем данные пользователя
            with transaction.atomic():
                user.email_verification_token = token
                user.email_verification_sent_at = timezone.now()
                user.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
            
            # Создаем контекст
            context = {
                'first_name': user.first_name,
                'verification_url': verify_url
            }
            
            return cls.send_email(
                template_name='email_verification',
                recipient_email=user.email,
                context=context,
                user=user
            )
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False

    @classmethod
    def send_password_reset(cls, user):
        """Отправка письма для сброса пароля"""
        from django.contrib.auth.tokens import default_token_generator
        from django.conf import settings
        
        # Создаем токен
        token = default_token_generator.make_token(user)
        # Сохраняем токен и время отправки
        user.password_reset_token = token
        user.password_reset_sent_at = timezone.now()
        user.save(update_fields=['password_reset_token', 'password_reset_sent_at'])
        
        # Формируем URL для API эндпоинта
        reset_url = f"{settings.SITE_URL}/api/users/auth/reset-password/"
        
        context = {
            'first_name': user.first_name,
            'email': user.email,
            'reset_url': reset_url,
            'token': token
        }
        
        return cls.send_email(
            template_name='password_reset',
            recipient_email=user.email,
            context=context,
            user=user
        )

    @classmethod
    def send_order_notification(cls, order, status_change=None):
        """Отправка уведомления о заказе"""
        template_map = {
            'processing': 'order_confirmation',
            'shipped': 'order_shipped',
            'delivered': 'order_delivered',
            'cancelled': 'order_cancelled'
        }
        
        template_name = template_map.get(order.status)
        if not template_name:
            return False
            
        context = {
            'user': order.user,
            'order': order,
            'status_change': status_change,
            'site_url': settings.SITE_URL
        }
        
        return cls.send_email(
            template_name=template_name,
            recipient_email=order.email,
            context=context,
            user=order.user
        )
    
    @classmethod
    def send_order_status_update_email(cls, order, status_change):
        """Отправка уведомления об обновлении статуса заказа"""
        template_map = {
            'processing': 'order_processing',
            'shipped': 'order_shipped',
            'delivered': 'order_delivered',
            'cancelled': 'order_cancelled'
        }

        template_name = template_map.get(status_change['to'])
        if not template_name:
            return False

        context = {
            'user': order.user,
            'order': order,
            'status_change': status_change,
            'site_url': settings.SITE_URL
        }

        return cls.send_email(
            template_name=template_name,
            recipient_email=order.email,
            context=context,
            user=order.user
        )
    
    @classmethod
    def retry_failed_email(cls, email_log_id):
        """Повторная отправка неудачного email"""
        try:
            email_log = EmailLog.objects.get(id=email_log_id, status=EmailLog.Status.FAILED)
            return cls.send_email(
                template_name=email_log.template.name,
                recipient_email=email_log.recipient_email,
                context=email_log.context,
                user=email_log.recipient
            )
        except EmailLog.DoesNotExist:
            return False