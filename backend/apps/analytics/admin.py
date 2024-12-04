from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
import csv
from datetime import datetime, timedelta
from .models import (
    SalesReport, ProductPerformance,
    CategoryPerformance, CustomerSegment
)
from .services import AnalyticsService

@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/analytics/sales_dashboard.html'
    
    list_display = (
        'date', 'report_type', 'total_sales',
        'total_orders', 'average_order_value',
        'return_rate', 'get_trend_indicator'
    )
    list_filter = (
        'report_type',
        ('date', admin.DateFieldListFilter),
    )
    readonly_fields = (
        'get_daily_comparison', 'get_weekly_comparison',
        'get_summary_chart'
    )
    
    actions = ['export_as_csv']
    
    fieldsets = (
        ('Основные метрики', {
            'fields': (
                'date', 'report_type', 'total_sales',
                'total_orders', 'average_order_value',
                'total_items_sold', 'get_summary_chart'
            )
        }),
        ('Клиенты', {
            'fields': (
                'new_customers', 'returning_customers'
            )
        }),
        ('Возвраты', {
            'fields': (
                'total_returns', 'returns_amount',
                'return_rate'
            )
        }),
        ('Финансы', {
            'fields': (
                'gross_revenue', 'net_revenue',
                'total_tax', 'total_shipping'
            )
        }),
        ('Доставка', {
            'fields': ('avg_delivery_time',)
        }),
        ('Конверсия', {
            'fields': (
                'conversion_rate',
                'cart_abandonment_rate'
            )
        }),
        ('Сравнение', {
            'fields': (
                'get_daily_comparison',
                'get_weekly_comparison'
            )
        })
    )

    def get_trend_indicator(self, obj):
        """Shows trend compared to previous day"""
        if obj.report_type != SalesReport.ReportType.DAILY:
            return '-'
            
        prev_date = obj.date - timedelta(days=1)
        prev_report = SalesReport.objects.filter(
            date=prev_date,
            report_type=obj.report_type
        ).first()
        
        if not prev_report:
            return '-'
            
        if obj.total_sales > prev_report.total_sales:
            return format_html(
                '<span style="color: green;">↑ {:.1f}%</span>',
                ((obj.total_sales - prev_report.total_sales) / prev_report.total_sales) * 100
            )
        elif obj.total_sales < prev_report.total_sales:
            return format_html(
                '<span style="color: red;">↓ {:.1f}%</span>',
                ((prev_report.total_sales - obj.total_sales) / prev_report.total_sales) * 100
            )
        return '→ 0%'
    get_trend_indicator.short_description = 'Тренд'

    def get_daily_comparison(self, obj):
        """Compare with previous day/week/month"""
        if not obj.date:
            return 'Дата не указана'
        
        if obj.report_type == SalesReport.ReportType.DAILY:
            prev_date = obj.date - timedelta(days=1)
        elif obj.report_type == SalesReport.ReportType.WEEKLY:
            prev_date = obj.date - timedelta(weeks=1)
        else:
            prev_date = obj.date - timedelta(days=30)
            
        prev_report = SalesReport.objects.filter(
            date=prev_date,
            report_type=obj.report_type
        ).first()
        
        if not prev_report:
            return 'Нет данных за предыдущий период'
            
        metrics = {
            'Продажи': (obj.total_sales, prev_report.total_sales),
            'Заказы': (obj.total_orders, prev_report.total_orders),
            'Новые клиенты': (obj.new_customers, prev_report.new_customers),
            'Возвраты': (obj.total_returns, prev_report.total_returns)
        }
        
        comparison = []
        for metric, (current, prev) in metrics.items():
            if prev:
                change = ((current - prev) / prev) * 100
                color = 'green' if change > 0 else 'red'
                comparison.append(
                    f'<span style="color: {color}">{metric}: {change:+.1f}%</span>'
                )
        
        return format_html('<br>'.join(comparison))
    get_daily_comparison.short_description = 'Сравнение с предыдущим периодом'

    def get_weekly_comparison(self, obj):
        """Compare with same period last week"""
        if not obj.date:
            return 'Дата не указана'
        
        if obj.report_type == SalesReport.ReportType.DAILY:
            prev_date = obj.date - timedelta(weeks=1)
        elif obj.report_type == SalesReport.ReportType.WEEKLY:
            prev_date = obj.date - timedelta(weeks=4)
        else:
            prev_date = obj.date - timedelta(days=365)
            
        prev_report = SalesReport.objects.filter(
            date=prev_date,
            report_type=obj.report_type
        ).first()
        
        if not prev_report:
            return 'Нет данных за аналогичный период'
            
        sales_diff = ((obj.total_sales - prev_report.total_sales) 
                     / prev_report.total_sales * 100)
        return format_html(
            '<span style="color: {}">{:+.1f}% к прошлому периоду</span>',
            'green' if sales_diff > 0 else 'red',
            sales_diff
        )
    get_weekly_comparison.short_description = 'Сравнение с аналогичным периодом'

    def get_summary_chart(self, obj):
        """Renders chart for the report"""
        if not obj:
            return ''
            
        # В реальном проекте здесь бы использовалась библиотека для визуализации
        return format_html(
            '<div id="summary-chart" data-report-id="{}"></div>',
            obj.id
        )
    get_summary_chart.short_description = 'График показателей'

    def changelist_view(self, request, extra_context=None):
        """Override to add dashboard data"""
        response = super().changelist_view(request, extra_context=extra_context)
        
        if hasattr(response, 'context_data'):
            # Получаем данные для дашборда
            dashboard_data = AnalyticsService.get_dashboard_data()
            response.context_data.update({
                'dashboard_data': dashboard_data,
                'title': 'Аналитика продаж'
            })
            
        return response

    def export_as_csv(self, request, queryset):
        """Export reports as CSV"""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=sales_report_{timezone.now()}.csv'
        writer = csv.writer(response)
        
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
            
        return response
    export_as_csv.short_description = 'Экспорт в CSV'

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'product_link', 'date', 'units_sold',
        'revenue', 'profit', 'return_rate'
    )
    list_filter = (
        'date',
        ('date', admin.DateFieldListFilter),
        'product__category'
    )
    search_fields = ('product__name', 'product__sku')
    
    readonly_fields = ('get_product_chart',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'product', 'date', 'get_product_chart'
            )
        }),
        ('Продажи', {
            'fields': (
                'units_sold', 'revenue', 'profit'
            )
        }),
        ('Возвраты', {
            'fields': (
                'returns', 'return_rate'
            )
        }),
        ('Рекомендации', {
            'fields': ('frequently_bought_with',)
        })
    )
    
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Товар'

    def get_product_chart(self, obj):
        """Renders chart for product performance"""
        if not obj:
            return ''
            
        return format_html(
            '<div id="product-chart" data-product-id="{}"></div>',
            obj.product.id
        )
    get_product_chart.short_description = 'График показателей'

@admin.register(CategoryPerformance)
class CategoryPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        'category_link', 'date', 'total_sales',
        'total_orders', 'average_order_value',
        'return_rate', 'get_trend'
    )
    list_filter = (
        'date',
        ('date', admin.DateFieldListFilter),
        'category'
    )
    
    readonly_fields = ('get_category_chart',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'category', 'date', 'get_category_chart'
            )
        }),
        ('Продажи', {
            'fields': (
                'total_sales', 'total_orders',
                'unique_customers', 'average_order_value'
            )
        }),
        ('Товары', {
            'fields': (
                'total_products', 'active_products',
                'out_of_stock_products'
            )
        }),
        ('Возвраты', {
            'fields': (
                'total_returns', 'return_rate'
            )
        })
    )

    def category_link(self, obj):
        url = reverse('admin:categories_category_change', args=[obj.category.id])
        return format_html('<a href="{}">{}</a>', url, obj.category.name)
    category_link.short_description = 'Категория'

    def get_trend(self, obj):
        """Shows trend compared to previous day"""
        prev_date = obj.date - timedelta(days=1)
        prev_perf = CategoryPerformance.objects.filter(
            date=prev_date,
            category=obj.category
        ).first()
        
        if not prev_perf:
            return '-'
            
        change = ((obj.total_sales - prev_perf.total_sales) 
                 / prev_perf.total_sales * 100)
        return format_html(
            '<span style="color: {}">{:+.1f}%</span>',
            'green' if change > 0 else 'red',
            change
        )
    get_trend.short_description = 'Тренд'

    def get_category_chart(self, obj):
        """Renders chart for category performance"""
        if not obj:
            return ''
            
        return format_html(
            '<div id="category-chart" data-category-id="{}"></div>',
            obj.category.id
        )
    get_category_chart.short_description = 'График показателей'

@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = (
        'user_link', 'get_rfm_score', 'total_spent',
        'purchase_frequency', 'last_purchase_date'
    )
    list_filter = (
        'recency_score', 'frequency_score',
        'monetary_score'
    )
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    
    readonly_fields = (
        'get_customer_chart',
        'get_segment_description'
    )
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user', 'get_segment_description',
                'get_customer_chart'
            )
        }),
        ('RFM Оценки', {
            'fields': (
                'recency_score', 'frequency_score',
                'monetary_score'
            )
        }),
        ('Метрики', {
            'fields': (
                'last_purchase_date', 'purchase_frequency',
                'total_spent', 'average_order_value',
                'total_orders', 'return_rate'
            )
        })
    )

    def user_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.email
        )
    user_link.short_description = 'Пользователь'

    def get_rfm_score(self, obj):
        """Shows RFM score with color coding"""
        scores = {
            5: 'darkgreen',
            4: 'green',
            3: 'orange',
            2: 'orangered',
            1: 'red'
        }
        
        return format_html(
            '<span style="color: {}">{}</span> | '
            '<span style="color: {}">{}</span> | '
            '<span style="color: {}">{}</span>',
            scores[obj.recency_score], f'R{obj.recency_score}',
            scores[obj.frequency_score], f'F{obj.frequency_score}',
            scores[obj.monetary_score], f'M{obj.monetary_score}'
        )
    get_rfm_score.short_description = 'RFM Score'

    def get_segment_description(self, obj):
        """Returns description of customer segment"""
        if obj.recency_score >= 4 and obj.frequency_score >= 4 and obj.monetary_score >= 4:
            return "Champions - Лучшие клиенты, высокая активность и ценность"
        elif obj.recency_score >= 3 and obj.frequency_score >= 3 and obj.monetary_score >= 3:
            return "Loyal Customers - Стабильные клиенты с хорошими показателями"
        elif obj.recency_score <= 2 and obj.frequency_score >= 3:
            return "At Risk - Ранее активные клиенты, требуют внимания"
        elif obj.recency_score <= 2 and obj.frequency_score <= 2:
            return "Lost - Потерянные клиенты, нужна реактивация"
        return "Regular - Обычные клиенты со средними показателями"
    get_segment_description.short_description = 'Сегмент'

    def get_customer_chart(self, obj):
        """Renders chart for customer activity"""
        if not obj:
            return ''
            
        return format_html(
            '<div id="customer-chart" data-customer-id="{}"></div>',
            obj.user.id
        )
    get_customer_chart.short_description = 'График активности'
