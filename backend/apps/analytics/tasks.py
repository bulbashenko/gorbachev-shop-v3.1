from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from .services import AnalyticsService
from django.conf import settings

def generate_daily_analytics():
    """Функция для ежедневной генерации аналитики"""
    service = AnalyticsService()
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Генерируем отчеты
    daily_report = service.generate_daily_report(yesterday)
    service.update_product_performance(yesterday)
    service.update_category_performance(yesterday)
    
    # Проверяем критические метрики
    if daily_report:
        alerts = []
        
        # Проверка падения продаж
        if daily_report.total_sales < 100:  # Пример порога
            alerts.append(f"Low sales alert: ${daily_report.total_sales}")
        
        # Проверка высокого процента возвратов
        if daily_report.return_rate > 10:  # Пример порога
            alerts.append(f"High return rate alert: {daily_report.return_rate}%")
        
        # Отправка уведомлений если есть алерты
        if alerts and hasattr(settings, 'ADMIN_EMAIL'):
            send_mail(
                subject=f'Analytics Alerts for {yesterday}',
                message='\n'.join(alerts),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True
            )
    
    return "Daily analytics generated successfully"

def generate_weekly_analytics():
    """Функция для еженедельной генерации аналитики"""
    service = AnalyticsService()
    end_date = timezone.now().date() - timedelta(days=1)
    
    weekly_report = service.generate_weekly_report(end_date)
    if weekly_report:
        # Здесь можно добавить отправку еженедельного отчета по email
        pass
    
    return "Weekly analytics generated successfully"

def generate_monthly_analytics():
    """Функция для ежемесячной генерации аналитики"""
    service = AnalyticsService()
    end_date = timezone.now().date() - timedelta(days=1)
    
    monthly_report = service.generate_monthly_report(end_date)
    if monthly_report:
        # Здесь можно добавить отправку ежемесячного отчета по email
        pass
    
    return "Monthly analytics generated successfully"

def update_customer_segments():
    """Функция для обновления сегментации клиентов"""
    service = AnalyticsService()
    service.update_customer_segments()
    return "Customer segments updated successfully"

def cleanup_old_reports():
    """Функция для очистки старых отчетов"""
    from .models import SalesReport, ProductPerformance, CategoryPerformance
    
    # Хранить ежедневные отчеты за последние 90 дней
    threshold_daily = timezone.now() - timedelta(days=90)
    SalesReport.objects.filter(
        report_type='daily',
        date__lt=threshold_daily
    ).delete()
    
    # Хранить еженедельные отчеты за последний год
    threshold_weekly = timezone.now() - timedelta(days=365)
    SalesReport.objects.filter(
        report_type='weekly',
        date__lt=threshold_weekly
    ).delete()
    
    # Очистка старых метрик производительности
    ProductPerformance.objects.filter(date__lt=threshold_daily).delete()
    CategoryPerformance.objects.filter(date__lt=threshold_daily).delete()
    
    return "Old reports cleaned up successfully"
