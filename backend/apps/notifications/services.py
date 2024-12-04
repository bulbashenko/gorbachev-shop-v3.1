from django.template import Template, Context
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
import logging
from .models import EmailTemplate, EmailLog
from .utils import run_async

logger = logging.getLogger('notifications')

class EmailService:
    BATCH_SIZE = 50  # Размер пакета для массовой отправки
    CACHE_TTL = 3600  # Время жизни кеша (1 час)

    @classmethod
    def _get_template(cls, template_name: str) -> EmailTemplate:
        """Получение шаблона с использованием кеша"""
        cache_key = f'email_template_{template_name}'
        template = cache.get(cache_key)
        
        if not template:
            try:
                template = EmailTemplate.objects.get(name=template_name)
                cache.set(cache_key, template, cls.CACHE_TTL)
            except EmailTemplate.DoesNotExist:
                logger.error(f"Email template '{template_name}' not found")
                raise
                
        return template

    @classmethod
    def _prepare_context_for_log(cls, context):
        """Подготовка контекста для сохранения в лог"""
        if not context:
            return {}
            
        prepared_context = {}
        for key, value in context.items():
            if key == 'user' and hasattr(value, 'id'):
                prepared_context[key] = {
                    'id': str(value.id),
                    'email': value.email,
                    'first_name': value.first_name,
                    'last_name': value.last_name
                }
            elif key == 'order' and hasattr(value, 'order_number'):
                prepared_context[key] = {
                    'order_number': value.order_number,
                    'status': value.status,
                    'total': str(value.total)
                }
            else:
                try:
                    from json import dumps
                    dumps({key: value})
                    prepared_context[key] = value
                except TypeError:
                    prepared_context[key] = str(value)
        
        return prepared_context

    @classmethod
    def _render_template(cls, template: EmailTemplate, context: dict) -> tuple:
        """Рендеринг шаблона с обработкой ошибок"""
        try:
            ctx = Context(context or {})
            subject = Template(template.subject).render(ctx)
            html_content = Template(template.html_content).render(ctx)
            text_content = Template(template.text_content).render(ctx)
            return subject, html_content, text_content
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            raise

    @classmethod
    @run_async
    def _send_email_async(cls, template_name: str, recipient_email: str, context: dict = None, user=None):
        """Асинхронная отправка email с улучшенной обработкой ошибок и повторными попытками"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                template = cls._get_template(template_name)
                log_context = cls._prepare_context_for_log(context)
                
                # Создаем лог с статусом PENDING
                email_log = EmailLog.objects.create(
                    template=template,
                    recipient=user,
                    recipient_email=recipient_email,
                    subject=Template(template.subject).render(Context(context or {})),
                    context=log_context,
                    status=EmailLog.Status.PENDING
                )
                
                try:
                    # Рендерим шаблон
                    subject, html_content, text_content = cls._render_template(template, context)
                    
                    # Отправляем email
                    connection = get_connection(
                        username=settings.EMAIL_HOST_USER,
                        password=settings.EMAIL_HOST_PASSWORD,
                        fail_silently=False
                    )
                    
                    send_mail(
                        subject=subject,
                        message=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient_email],
                        html_message=html_content,
                        connection=connection
                    )
                    
                    # Обновляем лог
                    email_log.status = EmailLog.Status.SENT
                    email_log.sent_at = timezone.now()
                    email_log.save()
                    
                    return True
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        email_log.status = EmailLog.Status.FAILED
                        email_log.error_message = str(e)
                        email_log.save()
                        logger.error(f"Failed to send email after {max_retries} attempts: {str(e)}")
                        return False
                    
                    logger.warning(f"Retry {retry_count} for email {email_log.id}: {str(e)}")
                    continue
                    
            except Exception as e:
                logger.error(f"Error in _send_email_async: {str(e)}")
                return False

    @classmethod
    def send_email(cls, template_name: str, recipient_email: str, context: dict = None, user=None):
        """Запуск асинхронной отправки email с улучшенной обработкой ошибок"""
        try:
            # Проверяем шаблон
            template = cls._get_template(template_name)
            log_context = cls._prepare_context_for_log(context or {})
            
            # Создаем запись в логе
            with transaction.atomic():
                EmailLog.objects.create(
                    template=template,
                    recipient=user,
                    recipient_email=recipient_email,
                    subject=Template(template.subject).render(Context(context or {})),
                    context=log_context,
                    status=EmailLog.Status.PENDING
                )
            
            # Запускаем асинхронную отправку
            cls._send_email_async(template_name, recipient_email, context, user)
            return True
            
        except Exception as e:
            logger.error(f"Error initiating email send: {str(e)}")
            return False

    @classmethod
    def send_verification_email(cls, user):
        """Отправка письма верификации с улучшенной обработкой токенов"""
        from django.contrib.auth.tokens import default_token_generator
        
        try:
            # Генерируем и сохраняем токен атомарно
            with transaction.atomic():
                token = default_token_generator.make_token(user)
                verify_url = f"{settings.SITE_URL}/api/users/auth/verify-email/?token={token}"
                
                user.email_verification_token = token
                user.email_verification_sent_at = timezone.now()
                user.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
            
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
        """Отправка письма для сброса пароля с улучшенной безопасностью"""
        from django.contrib.auth.tokens import default_token_generator
        
        try:
            # Генерируем и сохраняем токен атомарно
            with transaction.atomic():
                token = default_token_generator.make_token(user)
                reset_url = f"{settings.SITE_URL}/api/users/auth/reset-password/"
                
                user.password_reset_token = token
                user.password_reset_sent_at = timezone.now()
                user.save(update_fields=['password_reset_token', 'password_reset_sent_at'])
            
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
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False

    @classmethod
    def send_order_notification(cls, order):
        """Отправка уведомления о заказе с кешированием шаблонов"""
        try:
            logger.info(f"Sending order notification for order {order.order_number}")
            
            template_map = {
                'awaiting_payment': 'order_confirmation',
                'processing': 'order_processing',
                'confirmed': 'order_confirmed',
                'assembling': 'order_assembling',
                'shipped': 'order_shipped',
                'delivered': 'order_delivered',
                'cancelled': 'order_cancelled'
            }
            
            template_name = template_map.get(order.status, 'order_confirmation')
            
            context = {
                'user': order.user,
                'order': order,
                'site_url': settings.SITE_URL
            }
            
            return cls.send_email(
                template_name=template_name,
                recipient_email=order.email,
                context=context,
                user=order.user
            )
            
        except Exception as e:
            logger.error(f"Error sending order notification: {str(e)}")
            return False

    @classmethod
    def send_order_status_update_email(cls, order, status_change):
        """Отправка уведомления об обновлении статуса заказа"""
        try:
            context = {
                'user': order.user,
                'order': order,
                'status_change': {
                    'from': status_change.get('from'),
                    'to': status_change.get('to'),
                    'notes': status_change.get('notes')
                },
                'site_url': settings.SITE_URL
            }
            
            return cls.send_email(
                template_name='order_status_update',
                recipient_email=order.email,
                context=context,
                user=order.user
            )
            
        except Exception as e:
            logger.error(f"Error sending status update email: {str(e)}")
            return False
    
    @classmethod
    def retry_failed_email(cls, email_log_id):
        """Повторная отправка неудачного email с улучшенной обработкой ошибок"""
        try:
            with transaction.atomic():
                email_log = EmailLog.objects.select_for_update().get(
                    id=email_log_id,
                    status=EmailLog.Status.FAILED
                )
                
                # Обновляем статус на PENDING перед повторной отправкой
                email_log.status = EmailLog.Status.PENDING
                email_log.error_message = None
                email_log.save()
            
            return cls.send_email(
                template_name=email_log.template.name,
                recipient_email=email_log.recipient_email,
                context=email_log.context,
                user=email_log.recipient
            )
            
        except EmailLog.DoesNotExist:
            logger.error(f"Failed email log {email_log_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error retrying failed email: {str(e)}")
            return False

    @classmethod
    def process_email_queue(cls, batch_size=None):
        """Пакетная обработка очереди email"""
        batch_size = batch_size or cls.BATCH_SIZE
        
        try:
            pending_emails = EmailLog.objects.filter(
                status=EmailLog.Status.PENDING
            ).select_related(
                'template', 'recipient'
            )[:batch_size]
            
            for email in pending_emails:
                cls.send_email(
                    template_name=email.template.name,
                    recipient_email=email.recipient_email,
                    context=email.context,
                    user=email.recipient
                )
                
        except Exception as e:
            logger.error(f"Error processing email queue: {str(e)}")
