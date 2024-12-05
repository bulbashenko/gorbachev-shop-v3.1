from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()

class SalesReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class ReportType(models.TextChoices):
        DAILY = 'daily', _('Daily')
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')

    date = models.DateField()
    report_type = models.CharField(
        max_length=10,
        choices=ReportType.choices
    )
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_orders = models.IntegerField(default=0)
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_items_sold = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    total_returns = models.IntegerField(default=0)
    returns_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    return_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    gross_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    net_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_shipping = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    cart_abandonment_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    avg_delivery_time = models.IntegerField(
        help_text='Average delivery time in hours',
        default=0
    )

    class Meta:
        unique_together = ('date', 'report_type')
        indexes = [
            models.Index(fields=['date', 'report_type']),
            models.Index(fields=['total_sales']),
            models.Index(fields=['total_orders']),
            models.Index(fields=['conversion_rate']),
        ]

class ProductPerformance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='performance'
    )
    date = models.DateField()
    units_sold = models.IntegerField(default=0)
    revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    returns = models.IntegerField(default=0)
    return_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    purchase_count = models.IntegerField(default=0)
    frequently_bought_with = models.ManyToManyField(
        'products.Product',
        related_name='bought_with'
    )

    class Meta:
        unique_together = ('product', 'date')
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['units_sold']),
            models.Index(fields=['revenue']),
            models.Index(fields=['return_rate']),
        ]

class CategoryPerformance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='performance'
    )
    date = models.DateField()
    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_orders = models.IntegerField(default=0)
    unique_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_products = models.IntegerField(default=0)
    active_products = models.IntegerField(default=0)
    out_of_stock_products = models.IntegerField(default=0)
    total_returns = models.IntegerField(default=0)
    return_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    class Meta:
        unique_together = ('category', 'date')
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['total_sales']),
            models.Index(fields=['total_orders']),
            models.Index(fields=['return_rate']),
        ]

class CustomerSegment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='segment'
    )
    # RFM scores (1-5 scale)
    recency_score = models.IntegerField(default=1)
    frequency_score = models.IntegerField(default=1)
    monetary_score = models.IntegerField(default=1)
    
    # Actual values
    last_purchase_date = models.DateField(null=True)
    purchase_frequency = models.IntegerField(default=0)
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Additional metrics
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_orders = models.IntegerField(default=0)
    return_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['recency_score', 'frequency_score', 'monetary_score']),
            models.Index(fields=['last_purchase_date']),
            models.Index(fields=['total_spent']),
        ]

    def calculate_rfm_scores(self):
        """Расчет RFM-показателей"""
        from django.utils import timezone
        from django.db.models import Count, Sum, Avg
        from datetime import timedelta
        
        # Получаем заказы пользователя
        orders = self.user.orders.filter(
            status__in=['processing', 'shipped', 'delivered']
        )
        
        if not orders.exists():
            return
        
        # Recency
        last_order = orders.order_by('-created_at').first()
        days_since_last_order = (timezone.now().date() - last_order.created_at.date()).days
        
        if days_since_last_order <= 30:
            self.recency_score = 5
        elif days_since_last_order <= 60:
            self.recency_score = 4
        elif days_since_last_order <= 90:
            self.recency_score = 3
        elif days_since_last_order <= 180:
            self.recency_score = 2
        else:
            self.recency_score = 1
            
        # Frequency
        order_count = orders.count()
        if order_count >= 15:
            self.frequency_score = 5
        elif order_count >= 10:
            self.frequency_score = 4
        elif order_count >= 5:
            self.frequency_score = 3
        elif order_count >= 2:
            self.frequency_score = 2
        else:
            self.frequency_score = 1
            
        # Monetary
        total_spent = orders.aggregate(Sum('total'))['total__sum']
        if total_spent >= 1000:
            self.monetary_score = 5
        elif total_spent >= 500:
            self.monetary_score = 4
        elif total_spent >= 250:
            self.monetary_score = 3
        elif total_spent >= 100:
            self.monetary_score = 2
        else:
            self.monetary_score = 1
            
        # Обновляем метрики
        self.last_purchase_date = last_order.created_at.date()
        self.purchase_frequency = order_count
        self.total_spent = total_spent
        self.average_order_value = total_spent / order_count
        self.total_orders = order_count
        
        # Расчет процента возвратов
        returns = orders.filter(status='returned').count()
        self.return_rate = (returns / order_count * 100) if order_count > 0 else 0
        
        self.save()

    @staticmethod
    def get_segment_distribution():
        """Получение распределения клиентов по сегментам"""
        segments = CustomerSegment.objects.all()
        total = segments.count()
        
        if total == 0:
            return {}
            
        champions = segments.filter(
            recency_score__gte=4,
            frequency_score__gte=4,
            monetary_score__gte=4
        ).count()
        
        loyal = segments.filter(
            frequency_score__gte=3,
            monetary_score__gte=3
        ).exclude(
            recency_score__gte=4,
            frequency_score__gte=4,
            monetary_score__gte=4
        ).count()
        
        at_risk = segments.filter(
            recency_score__lte=2,
            frequency_score__gte=3
        ).count()
        
        lost = segments.filter(
            recency_score=1,
            frequency_score__lte=2
        ).count()
        
        return {
            'champions': round(champions / total * 100, 2),
            'loyal': round(loyal / total * 100, 2),
            'at_risk': round(at_risk / total * 100, 2),
            'lost': round(lost / total * 100, 2),
            'other': round(
                (total - champions - loyal - at_risk - lost) / total * 100,
                2
            )
        }
