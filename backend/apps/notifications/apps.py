from django.apps import AppConfig
from django.db import ProgrammingError, OperationalError

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'

    def ready(self):
        try:
            from .models import EmailTemplate
            
            # Проверяем существование таблицы
            EmailTemplate.objects.exists()
            
            # Создаем все необходимые шаблоны заказов
            default_templates = [
                {
                    'name': 'order_confirmation',
                    'subject': 'Order Confirmation - {{ order.order_number }}',
                    'html_content': '''
                    {% extends "notifications/email/base.html" %}
                    {% block content %}
                    <h2>Order Confirmed</h2>
                    <p>Thank you for your order!</p>
                    <p>Order #{{ order.order_number }}</p>
                    <p>Total: ${{ order.total }}</p>
                    {% endblock %}
                    ''',
                    'text_content': 'Order Confirmation - {{ order.order_number }}'
                },
                {
                    'name': 'order_processing',
                    'subject': 'Order Processing - {{ order.order_number }}',
                    'html_content': '''
                    {% extends "notifications/email/base.html" %}
                    {% block content %}
                    <h2>Order Processing</h2>
                    <p>Your order is being processed.</p>
                    <p>Order #{{ order.order_number }}</p>
                    {% endblock %}
                    ''',
                    'text_content': 'Order Processing - {{ order.order_number }}'
                },
                {
                    'name': 'order_confirmed',
                    'subject': 'Order Confirmed - {{ order.order_number }}',
                    'html_content': '''
                    {% extends "notifications/email/base.html" %}
                    {% block content %}
                    <h2>Order Confirmed</h2>
                    <p>Your order has been confirmed.</p>
                    <p>Order #{{ order.order_number }}</p>
                    {% endblock %}
                    ''',
                    'text_content': 'Order Confirmed - {{ order.order_number }}'
                },
                {
                    'name': 'order_shipped',
                    'subject': 'Order Shipped - {{ order.order_number }}',
                    'html_content': '''
                    {% extends "notifications/email/base.html" %}
                    {% block content %}
                    <h2>Order Shipped</h2>
                    <p>Your order has been shipped!</p>
                    <p>Order #{{ order.order_number }}</p>
                    <p>Tracking: {{ order.tracking_number }}</p>
                    {% endblock %}
                    ''',
                    'text_content': 'Order Shipped - {{ order.order_number }}'
                },
                {
                    'name': 'order_delivered',
                    'subject': 'Order Delivered - {{ order.order_number }}',
                    'html_content': '''
                    {% extends "notifications/email/base.html" %}
                    {% block content %}
                    <h2>Order Delivered</h2>
                    <p>Your order has been delivered!</p>
                    <p>Order #{{ order.order_number }}</p>
                    {% endblock %}
                    ''',
                    'text_content': 'Order Delivered - {{ order.order_number }}'
                }
            ]

            # Создаем шаблоны, если они не существуют
            for template in default_templates:
                EmailTemplate.objects.get_or_create(
                    name=template['name'],
                    defaults=template
                )
                
        except (ProgrammingError, OperationalError):
            pass