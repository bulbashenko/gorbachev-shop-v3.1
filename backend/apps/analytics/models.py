from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Avg, Q, F
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta, datetime
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
import uuid

User = get_user_model()

class SalesReport(models.Model):
    """Модель для хранения агрегированных данных по продажам"""
    class ReportType(models.TextChoices):
        DAILY = 'daily', 'Daily Report'
        WEEKLY = 'weekly', 'Weekly Report'
        MONTHLY = 'monthly', 'Monthly Report'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date = models.DateField()
    report_type = models.CharField(
        max_length=10,
        choices=ReportType.choices,
        default=ReportType.DAILY
    )
    
    # Основные метрики
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)
    
    # Метрики по клиентам
    new_customers = models.IntegerField(default=0)
    returning_customers = models.IntegerField(default=0)
    cancelled_orders = models.IntegerField(default=0)
    
    # Финансовые показатели
    gross_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Метрики возвратов
    total_returns = models.IntegerField(default=0)
    returns_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Конверсия
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cart_abandonment_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Время доставки
    avg_delivery_time = models.IntegerField(
        default=0,
        help_text='Average delivery time in hours'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'report_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'report_type'],
                name='unique_report_date'
            )
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} Report {self.date}"

    @classmethod
    def get_cached_report(cls, date, report_type='daily'):
        """Получение отчета из кеша или БД"""
        cache_key = f'sales_report_{report_type}_{date}'
        report = cache.get(cache_key)
        
        if not report:
            report = cls.objects.filter(
                date=date,
                report_type=report_type
            ).first()
            if report:
                cache.set(cache_key, report, 3600)  # кешируем на час
                
        return report

class ProductPerformance(models.Model):
    """Модель для отслеживания эффективности продуктов"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    date = models.DateField()
    
    # Продажи
    units_sold = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Возвраты
    returns = models.IntegerField(default=0)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Статистика просмотров
    views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    
    # Конверсия
    add_to_cart_count = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Комбинации
    frequently_bought_with = models.ManyToManyField(
        Product,
        related_name='bought_with',
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'date')
        indexes = [
            models.Index(fields=['date', 'product']),
            models.Index(fields=['revenue']),
            models.Index(fields=['units_sold']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.date}"

    def calculate_metrics(self):
        """Расчет метрик"""
        if self.views > 0:
            self.conversion_rate = (self.purchase_count / self.views) * 100
        if self.units_sold > 0:
            self.return_rate = (self.returns / self.units_sold) * 100
        self.save()

    @classmethod
    def get_cached_performance(cls, product_id, date):
        """Получение метрик из кеша или БД"""
        cache_key = f'product_performance_{product_id}_{date}'
        performance = cache.get(cache_key)
        
        if not performance:
            performance = cls.objects.filter(
                product_id=product_id,
                date=date
            ).first()
            if performance:
                cache.set(cache_key, performance, 3600)
                
        return performance

class CategoryPerformance(models.Model):
    """Модель для анализа эффективности категорий"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    date = models.DateField()
    
    # Основные метрики
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    unique_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Метрики товаров
    total_products = models.IntegerField(default=0)
    active_products = models.IntegerField(default=0)
    out_of_stock_products = models.IntegerField(default=0)
    
    # Возвраты
    total_returns = models.IntegerField(default=0)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('category', 'date')
        indexes = [
            models.Index(fields=['date', 'category']),
            models.Index(fields=['total_sales']),
        ]

    def __str__(self):
        return f"{self.category.name} - {self.date}"

    @classmethod
    def get_cached_performance(cls, category_id, date):
        """Получение метрик из кеша или БД"""
        cache_key = f'category_performance_{category_id}_{date}'
        performance = cache.get(cache_key)
        
        if not performance:
            performance = cls.objects.filter(
                category_id=category_id,
                date=date
            ).first()
            if performance:
                cache.set(cache_key, performance, 3600)
                
        return performance

class CustomerSegment(models.Model):
    """Модель для сегментации клиентов на основе RFM"""
    class RFMScore(models.IntegerChoices):
        ONE = 1, 'Low'
        TWO = 2, 'Medium-Low'
        THREE = 3, 'Medium'
        FOUR = 4, 'Medium-High'
        FIVE = 5, 'High'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='rfm_segment'
    )
    
    # RFM scores
    recency_score = models.IntegerField(
        choices=RFMScore.choices,
        default=RFMScore.THREE
    )
    frequency_score = models.IntegerField(
        choices=RFMScore.choices,
        default=RFMScore.THREE
    )
    monetary_score = models.IntegerField(
        choices=RFMScore.choices,
        default=RFMScore.THREE
    )
    
    # Actual values
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    purchase_frequency = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Дополнительные метрики
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    products_bought = models.IntegerField(default=0)
    categories_bought = models.IntegerField(default=0)
    
    # Метрики оттока
    days_since_last_purchase = models.IntegerField(default=0)
    is_churned = models.BooleanField(default=False)
    churn_probability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['recency_score', 'frequency_score', 'monetary_score']),
            models.Index(fields=['is_churned']),
        ]

    def __str__(self):
        return f"RFM Segment for {self.user.email}"

    def calculate_rfm_scores(self):
        """Расчет RFM-скоров"""
        now = timezone.now()
        
        # Получаем все заказы пользователя
        orders = Order.objects.filter(
            user=self.user,
            status='delivered'
        ).order_by('-created_at')
        
        if orders.exists():
            # Recency
            self.last_purchase_date = orders.first().created_at
            days_since_purchase = (now - self.last_purchase_date).days
            self.days_since_last_purchase = days_since_purchase
            
            # Frequency
            self.purchase_frequency = orders.count()
            
            # Monetary
            self.total_spent = orders.aggregate(
                total=Sum('total')
            )['total'] or 0
            
            # Дополнительные метрики
            self.average_order_value = self.total_spent / self.purchase_frequency
            self.products_bought = OrderItem.objects.filter(
                order__in=orders
            ).values('variant__product').distinct().count()
            self.categories_bought = OrderItem.objects.filter(
                order__in=orders
            ).values('variant__product__category').distinct().count()
            
            # Определение скоров
            self.recency_score = self._calculate_recency_score(days_since_purchase)
            self.frequency_score = self._calculate_frequency_score()
            self.monetary_score = self._calculate_monetary_score()
            
            # Проверка на отток
            self._check_churn_status()
            
        self.save()

    def _calculate_recency_score(self, days):
        """Расчет скора свежести"""
        if days <= 30:
            return self.RFMScore.FIVE
        elif days <= 60:
            return self.RFMScore.FOUR
        elif days <= 90:
            return self.RFMScore.THREE
        elif days <= 180:
            return self.RFMScore.TWO
        return self.RFMScore.ONE

    def _calculate_frequency_score(self):
        """Расчет скора частоты"""
        if self.purchase_frequency >= 20:
            return self.RFMScore.FIVE
        elif self.purchase_frequency >= 10:
            return self.RFMScore.FOUR
        elif self.purchase_frequency >= 5:
            return self.RFMScore.THREE
        elif self.purchase_frequency >= 2:
            return self.RFMScore.TWO
        return self.RFMScore.ONE

    def _calculate_monetary_score(self):
        """Расчет денежного скора"""
        if self.total_spent >= 1000:
            return self.RFMScore.FIVE
        elif self.total_spent >= 500:
            return self.RFMScore.FOUR
        elif self.total_spent >= 250:
            return self.RFMScore.THREE
        elif self.total_spent >= 100:
            return self.RFMScore.TWO
        return self.RFMScore.ONE

    def _check_churn_status(self):
        """Проверка статуса оттока"""
        # Базовая логика: клиент считается ушедшим, если не совершал покупок 180 дней
        CHURN_THRESHOLD = 180
        
        if self.days_since_last_purchase > CHURN_THRESHOLD:
            self.is_churned = True
            # Простая формула для вероятности оттока
            self.churn_probability = min(
                (self.days_since_last_purchase / CHURN_THRESHOLD) * 100,
                100
            )
        else:
            self.is_churned = False
            self.churn_probability = max(
                (self.days_since_last_purchase / CHURN_THRESHOLD) * 50,
                0
            )

    @classmethod
    def get_segment_distribution(cls):
        """Получение распределения клиентов по сегментам"""
        return {
            'champions': cls.objects.filter(
                recency_score__gte=4,
                frequency_score__gte=4,
                monetary_score__gte=4
            ).count(),
            'loyal': cls.objects.filter(
                recency_score__gte=3,
                frequency_score__gte=3,
                monetary_score__gte=3
            ).exclude(
                recency_score__gte=4,
                frequency_score__gte=4,
                monetary_score__gte=4
            ).count(),
            'potential': cls.objects.filter(
                recency_score__gte=3,
                frequency_score__lt=3,
                monetary_score__gte=3
            ).count(),
            'at_risk': cls.objects.filter(
                recency_score__lte=2,
                frequency_score__gte=3
            ).count(),
            'lost': cls.objects.filter(
                recency_score=1,
                frequency_score__lte=2
            ).count(),
        }