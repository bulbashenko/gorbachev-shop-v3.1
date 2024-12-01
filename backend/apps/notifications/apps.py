# apps/notifications/apps.py

from django.apps import AppConfig
from django.db import ProgrammingError, OperationalError


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'

    def ready(self):
        try:
            # Импортируем модель здесь, чтобы избежать circular import
            from .models import EmailTemplate
            
            # Проверяем существование таблицы
            EmailTemplate.objects.exists()
            
            # Если таблица существует, создаем шаблоны
            self.create_default_templates()
        except (ProgrammingError, OperationalError):
            # Таблица еще не создана (например, при первом запуске)
            pass

    def create_default_templates(self):
        from .models import EmailTemplate
        from django.db import transaction

        default_templates = [
            {
                'name': 'email_verification',
                'subject': 'Verify Your Email Address',
                'html_content': '''
{% extends "notifications/email/base.html" %}
{% block title %}Verify Your Email Address{% endblock %}
{% block content %}
<p>Hi {{ user.first_name }},</p>
<p>Welcome! Please verify your email address by clicking the button below:</p>
<p style="text-align: center;">
    <a href="{{ verification_url }}" class="button">Verify Email</a>
</p>
<p>This link will expire in 24 hours.</p>
{% endblock %}
                ''',
                'text_content': '''
Hi {{ user.first_name }},

Welcome! Please verify your email address by clicking the link below:

{{ verification_url }}

This link will expire in 24 hours.
                '''
            },
            {
                'name': 'password_reset',
                'subject': 'Reset Your Password',
                'html_content': '''
{% extends "notifications/email/base.html" %}
{% block title %}Reset Your Password{% endblock %}
{% block content %}
<p>Hi {{ user.first_name }},</p>
<p>Click the button below to reset your password:</p>
<p style="text-align: center;">
    <a href="{{ reset_url }}" class="button">Reset Password</a>
</p>
<p>This link will expire in 1 hour.</p>
<p>If you didn't request this, you can safely ignore this email.</p>
{% endblock %}
                ''',
                'text_content': '''
Hi {{ user.first_name }},

Click the link below to reset your password:

{{ reset_url }}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.
                '''
            },
            {
                'name': 'order_confirmation',
                'subject': 'Order Confirmation - {{ order.order_number }}',
                'html_content': '''
{% extends "notifications/email/base.html" %}
{% block title %}Order Confirmation{% endblock %}
{% block content %}
<p>Hi {{ user.first_name }},</p>
<p>Thank you for your order! Here are your order details:</p>
<p><strong>Order Number:</strong> {{ order.order_number }}</p>
<p><strong>Total Amount:</strong> {{ order.total }}</p>
{% endblock %}
                ''',
                'text_content': '''
Hi {{ user.first_name }},

Thank you for your order! Here are your order details:

Order Number: {{ order.order_number }}
Total Amount: {{ order.total }}
                '''
            }
        ]

        with transaction.atomic():
            for template_data in default_templates:
                EmailTemplate.objects.get_or_create(
                    name=template_data['name'],
                    defaults={
                        'subject': template_data['subject'],
                        'html_content': template_data['html_content'].strip(),
                        'text_content': template_data['text_content'].strip()
                    }
                )