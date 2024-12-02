from django.db.models import Sum, Count, Avg, F, Q, ExpressionWrapper, fields
from django.contrib.auth import get_user_model

User = get_user_model()
from django.db.models.functions import TruncDate, ExtractHour, Now
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta, datetime
from decimal import Decimal
from typing import Dict, List, Optional
import pandas as pd

from .models import (
    SalesReport, ProductPerformance,
    CategoryPerformance, CustomerSegment
)
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem

class AnalyticsService:
    @staticmethod
    def generate_daily_report(date=None):
        """Генерация ежедневного отчета по продажам"""
        if not date:
            date = timezone.now().date()

        # Получаем заказы за день с оптимизированными запросами
        daily_orders = Order.objects.filter(
            created_at__date=date
        ).select_related('user').prefetch_related('items')

        completed_orders = daily_orders.filter(
            status__in=['processing', 'shipped', 'delivered']
        )

        # Агрегированные метрики заказов
        order_metrics = completed_orders.aggregate(
            total_sales=Sum('total'),
            total_tax=Sum('tax'),
            total_shipping=Sum('shipping_cost'),
            total_items=Sum('items__quantity'),
            total_returns=Count('id', filter=Q(status='returned')),
            returns_amount=Sum('total', filter=Q(status='returned')),
            avg_delivery_hours=Avg(
                ExpressionWrapper(
                    F('delivered_at') - F('created_at'),
                    output_field=fields.DurationField()
                ),
                filter=Q(delivered_at__isnull=False)
            )
        )

        # Анализ клиентов
        customer_stats = completed_orders.values('user').annotate(
            order_count=Count('id')
        )
        
        # Конверсия
        total_sessions = Cart.objects.filter(
            created_at__date=date
        ).count()
        
        abandoned_carts = Cart.objects.filter(
            created_at__date=date,
            items__isnull=False,
            order__isnull=True
        ).count()

        # Создаем или обновляем отчет
        report, _ = SalesReport.objects.update_or_create(
            date=date,
            report_type=SalesReport.ReportType.DAILY,
            defaults={
                'total_sales': order_metrics['total_sales'] or 0,
                'total_orders': completed_orders.count(),
                'average_order_value': (
                    order_metrics['total_sales'] / completed_orders.count()
                    if completed_orders.exists() else 0
                ),
                'total_items_sold': order_metrics['total_items'] or 0,
                'new_customers': customer_stats.filter(order_count=1).count(),
                'returning_customers': customer_stats.filter(order_count__gt=1).count(),
                'cancelled_orders': daily_orders.filter(status='cancelled').count(),
                'total_returns': order_metrics['total_returns'] or 0,
                'returns_amount': order_metrics['returns_amount'] or 0,
                'return_rate': (
                    (order_metrics['total_returns'] or 0) / completed_orders.count() * 100
                    if completed_orders.exists() else 0
                ),
                'gross_revenue': order_metrics['total_sales'] or 0,
                'net_revenue': (
                    (order_metrics['total_sales'] or 0) -
                    (order_metrics['total_tax'] or 0) -
                    (order_metrics['total_shipping'] or 0)
                ),
                'total_tax': order_metrics['total_tax'] or 0,
                'total_shipping': order_metrics['total_shipping'] or 0,
                'conversion_rate': (
                    completed_orders.count() / total_sessions * 100
                    if total_sessions > 0 else 0
                ),
                'cart_abandonment_rate': (
                    abandoned_carts / (abandoned_carts + completed_orders.count()) * 100
                    if (abandoned_carts + completed_orders.count()) > 0 else 0
                ),
                'avg_delivery_time': (
                    order_metrics['avg_delivery_hours'].total_seconds() // 3600
                    if order_metrics['avg_delivery_hours'] else 0
                )
            }
        )

        # Кешируем отчет
        cache_key = f'sales_report_daily_{date}'
        cache.set(cache_key, report, 3600)

        return report

    @staticmethod
    def generate_weekly_report(date=None):
        """Генерация еженедельного отчета"""
        if not date:
            date = timezone.now().date()
        
        # Находим начало недели
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Агрегируем ежедневные отчеты
        daily_reports = SalesReport.objects.filter(
            date__range=[start_of_week, end_of_week],
            report_type=SalesReport.ReportType.DAILY
        )

        if not daily_reports.exists():
            return None

        report_metrics = daily_reports.aggregate(
            total_sales=Sum('total_sales'),
            total_orders=Sum('total_orders'),
            total_items_sold=Sum('total_items_sold'),
            new_customers=Sum('new_customers'),
            returning_customers=Sum('returning_customers'),
            total_returns=Sum('total_returns'),
            returns_amount=Sum('returns_amount'),
            gross_revenue=Sum('gross_revenue'),
            net_revenue=Sum('net_revenue')
        )

        report, _ = SalesReport.objects.update_or_create(
            date=start_of_week,
            report_type=SalesReport.ReportType.WEEKLY,
            defaults={
                'total_sales': report_metrics['total_sales'] or 0,
                'total_orders': report_metrics['total_orders'] or 0,
                'average_order_value': (
                    report_metrics['total_sales'] / report_metrics['total_orders']
                    if report_metrics['total_orders'] else 0
                ),
                'total_items_sold': report_metrics['total_items_sold'] or 0,
                'new_customers': report_metrics['new_customers'] or 0,
                'returning_customers': report_metrics['returning_customers'] or 0,
                'total_returns': report_metrics['total_returns'] or 0,
                'returns_amount': report_metrics['returns_amount'] or 0,
                'gross_revenue': report_metrics['gross_revenue'] or 0,
                'net_revenue': report_metrics['net_revenue'] or 0
            }
        )
        
        return report

    @staticmethod
    def generate_monthly_report(date=None):
        """Генерация ежемесячного отчета"""
        if not date:
            date = timezone.now().date()
        
        # Находим начало и конец месяца
        start_of_month = date.replace(day=1)
        if start_of_month.month == 12:
            end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)

        # Агрегируем ежедневные отчеты
        daily_reports = SalesReport.objects.filter(
            date__range=[start_of_month, end_of_month],
            report_type=SalesReport.ReportType.DAILY
        )

        if not daily_reports.exists():
            return None

        report_metrics = daily_reports.aggregate(
            total_sales=Sum('total_sales'),
            total_orders=Sum('total_orders'),
            total_items_sold=Sum('total_items_sold'),
            new_customers=Sum('new_customers'),
            returning_customers=Sum('returning_customers'),
            total_returns=Sum('total_returns'),
            returns_amount=Sum('returns_amount'),
            gross_revenue=Sum('gross_revenue'),
            net_revenue=Sum('net_revenue')
        )

        report, _ = SalesReport.objects.update_or_create(
            date=start_of_month,
            report_type=SalesReport.ReportType.MONTHLY,
            defaults={
                'total_sales': report_metrics['total_sales'] or 0,
                'total_orders': report_metrics['total_orders'] or 0,
                'average_order_value': (
                    report_metrics['total_sales'] / report_metrics['total_orders']
                    if report_metrics['total_orders'] else 0
                ),
                'total_items_sold': report_metrics['total_items_sold'] or 0,
                'new_customers': report_metrics['new_customers'] or 0,
                'returning_customers': report_metrics['returning_customers'] or 0,
                'total_returns': report_metrics['total_returns'] or 0,
                'returns_amount': report_metrics['returns_amount'] or 0,
                'gross_revenue': report_metrics['gross_revenue'] or 0,
                'net_revenue': report_metrics['net_revenue'] or 0
            }
        )
        
        return report

    @staticmethod
    def update_product_performance(date=None):
        """Обновление статистики по продуктам"""
        if not date:
            date = timezone.now().date()

        # Оптимизированный запрос для получения продаж
        sales_data = OrderItem.objects.filter(
            order__created_at__date=date,
            order__status__in=['processing', 'shipped', 'delivered']
        ).values(
            'variant__product'
        ).annotate(
            units_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity')),
            returns=Count('order', filter=Q(order__status='returned')),
            orders=Count('order', distinct=True)
        ).select_related('variant__product')

        for data in sales_data:
            product = Product.objects.get(id=data['variant__product'])
            
            # Расчет прибыли
            profit = Decimal('0.00')
            if hasattr(product, 'cost_price'):
                profit = data['revenue'] - (product.cost_price * data['units_sold'])

            performance, _ = ProductPerformance.objects.update_or_create(
                product=product,
                date=date,
                defaults={
                    'units_sold': data['units_sold'],
                    'revenue': data['revenue'],
                    'profit': profit,
                    'returns': data['returns'],
                    'return_rate': (
                        (data['returns'] / data['units_sold']) * 100
                        if data['units_sold'] > 0 else 0
                    ),
                    'purchase_count': data['orders']
                }
            )

            # Обновляем часто покупаемые вместе товары
            related_products = OrderItem.objects.filter(
                order__in=OrderItem.objects.filter(
                    variant__product=product,
                    order__created_at__date=date
                ).values('order')
            ).exclude(
                variant__product=product
            ).values(
                'variant__product'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            performance.frequently_bought_with.set(
                [p['variant__product'] for p in related_products]
            )

            # Кешируем результаты
            cache_key = f'product_performance_{product.id}_{date}'
            cache.set(cache_key, performance, 3600)

    @staticmethod
    def update_category_performance(date=None):
        """Обновление статистики по категориям"""
        if not date:
            date = timezone.now().date()

        categories = Category.objects.all()
        
        for category in categories:
            # Оптимизированный запрос для получения данных о заказах
            orders_data = Order.objects.filter(
                created_at__date=date,
                status__in=['processing', 'shipped', 'delivered'],
                items__variant__product__category=category
            ).aggregate(
                total_sales=Sum('total'),
                total_orders=Count('id', distinct=True),
                unique_customers=Count('user', distinct=True),
                total_returns=Count('id', filter=Q(status='returned')),
            )

            # Получаем данные о товарах
            products_data = Product.objects.filter(
                category=category
            ).aggregate(
                total_products=Count('id'),
                active_products=Count('id', filter=Q(is_active=True)),
                out_of_stock=Count(
                    'id',
                    filter=Q(variants__stock=0) | Q(variants__isnull=True)
                )
            )

            performance, _ = CategoryPerformance.objects.update_or_create(
                category=category,
                date=date,
                defaults={
                    'total_sales': orders_data['total_sales'] or 0,
                    'total_orders': orders_data['total_orders'] or 0,
                    'unique_customers': orders_data['unique_customers'] or 0,
                    'average_order_value': (
                        orders_data['total_sales'] / orders_data['total_orders']
                        if orders_data['total_orders'] else 0
                    ),
                    'total_products': products_data['total_products'],
                    'active_products': products_data['active_products'],
                    'out_of_stock_products': products_data['out_of_stock'],
                    'total_returns': orders_data['total_returns'] or 0,
                    'return_rate': (
                        (orders_data['total_returns'] / orders_data['total_orders']) * 100
                        if orders_data['total_orders'] else 0
                    )
                }
            )

            # Кешируем результаты
            cache_key = f'category_performance_{category.id}_{date}'
            cache.set(cache_key, performance, 3600)

    @staticmethod
    def update_customer_segments():
        """Обновление RFM-сегментов клиентов"""
        users = User.objects.filter(is_active=True)
        
        for user in users:
            segment, _ = CustomerSegment.objects.get_or_create(user=user)
            segment.calculate_rfm_scores()

    @staticmethod
    def export_report_to_excel(report_type: str, start_date: datetime, end_date: datetime) -> bytes:
        """Экспорт отчета в Excel"""
        reports = SalesReport.objects.filter(
            report_type=report_type,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Создаем DataFrame
        data = []
        for report in reports:
            data.append({
                'Date': report.date,
                'Total Sales': report.total_sales,
                'Total Orders': report.total_orders,
                'Average Order Value': report.average_order_value,
                'New Customers': report.new_customers,
                'Returning Customers': report.returning_customers,
                'Total Returns': report.total_returns,
                'Return Rate': f"{report.return_rate}%",
                'Conversion Rate': f"{report.conversion_rate}%",
                'Gross Revenue': report.gross_revenue,
                'Net Revenue': report.net_revenue
            })

        df = pd.DataFrame(data)
        
        # Создаем Excel файл в памяти
        output = pd.ExcelWriter('report.xlsx', engine='xlsxwriter')
        df.to_excel(output, sheet_name='Sales Report', index=False)
        
        # Получаем бинарные данные
        output.save()
        with open('report.xlsx', 'rb') as f:
            excel_data = f.read()
        
        return excel_data

    @staticmethod
    def get_dashboard_data() -> Dict:
        """Получение данных для дашборда"""
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Получаем основные метрики за 30 дней
        report_metrics = SalesReport.objects.filter(
            date__range=[thirty_days_ago, today],
            report_type=SalesReport.ReportType.DAILY
        ).aggregate(
            total_sales=Sum('total_sales'),
            total_orders=Sum('total_orders'),
            total_returns=Sum('total_returns'),
            new_customers=Sum('new_customers')
        )

        # Получаем тренды продаж по дням
        sales_trend = list(SalesReport.objects.filter(
            date__range=[thirty_days_ago, today],
            report_type=SalesReport.ReportType.DAILY
        ).order_by('date').values('date', 'total_sales'))

        # Топ продуктов
        top_products = ProductPerformance.objects.filter(
            date__range=[thirty_days_ago, today]
        ).values(
            'product__name'
        ).annotate(
            total_revenue=Sum('revenue'),
            total_units=Sum('units_sold')
        ).order_by('-total_revenue')[:5]

        # Распределение по категориям
        category_distribution = CategoryPerformance.objects.filter(
            date__range=[thirty_days_ago, today]
        ).values(
            'category__name'
        ).annotate(
            total_sales=Sum('total_sales'),
            total_orders=Sum('total_orders')
        ).order_by('-total_sales')

        # RFM-сегменты
        rfm_distribution = CustomerSegment.get_segment_distribution()

        return {
            'summary': {
                'total_sales': report_metrics['total_sales'],
                'total_orders': report_metrics['total_orders'],
                'total_returns': report_metrics['total_returns'],
                'new_customers': report_metrics['new_customers']
            },
            'sales_trend': sales_trend,
            'top_products': list(top_products),
            'category_distribution': list(category_distribution),
            'rfm_distribution': rfm_distribution
        }