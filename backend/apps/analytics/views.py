from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
from django.http import HttpResponse
from .models import SalesReport, ProductPerformance, CategoryPerformance, CustomerSegment
from .serializers import (
    SalesReportSerializer, ProductPerformanceSerializer,
    CategoryPerformanceSerializer, CustomerSegmentSerializer,
    DashboardSerializer, ChartDataSerializer
)
from .services import AnalyticsService

class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet для аналитики"""
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Получение данных для дашборда"""
        dashboard_data = AnalyticsService.get_dashboard_data()
        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        """Получение отчета о продажах"""
        try:
            start_date = datetime.strptime(
                request.query_params.get('start_date'),
                '%Y-%m-%d'
            ).date()
            end_date = datetime.strptime(
                request.query_params.get('end_date'),
                '%Y-%m-%d'
            ).date()
            report_type = request.query_params.get('type', 'daily')
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reports = SalesReport.objects.filter(
            date__range=[start_date, end_date],
            report_type=report_type
        ).order_by('date')

        serializer = SalesReportSerializer(reports, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def product_performance(self, request):
        """Получение статистики по продуктам"""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        performance = ProductPerformance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('product', 'product__category')

        serializer = ProductPerformanceSerializer(performance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def category_performance(self, request):
        """Получение статистики по категориям"""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        performance = CategoryPerformance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('category')

        serializer = CategoryPerformanceSerializer(performance, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def customer_segments(self, request):
        """Получение сегментации клиентов"""
        segments = CustomerSegment.objects.all().select_related('user')
        
        # Фильтрация по параметрам
        segment_type = request.query_params.get('segment')
        if segment_type:
            if segment_type == 'champions':
                segments = segments.filter(
                    recency_score__gte=4,
                    frequency_score__gte=4,
                    monetary_score__gte=4
                )
            elif segment_type == 'at_risk':
                segments = segments.filter(
                    recency_score__lte=2,
                    frequency_score__gte=3
                )
            elif segment_type == 'lost':
                segments = segments.filter(
                    recency_score=1,
                    frequency_score__lte=2
                )

        serializer = CustomerSegmentSerializer(segments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_report(self, request):
        """Экспорт отчета в Excel"""
        try:
            start_date = datetime.strptime(
                request.query_params.get('start_date'),
                '%Y-%m-%d'
            ).date()
            end_date = datetime.strptime(
                request.query_params.get('end_date'),
                '%Y-%m-%d'
            ).date()
            report_type = request.query_params.get('type', 'daily')
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        excel_data = AnalyticsService.export_report_to_excel(
            report_type,
            start_date,
            end_date
        )

        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=report_{start_date}_{end_date}.xlsx'
        
        return response

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """Получение данных для графиков"""
        chart_type = request.query_params.get('type')
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        if chart_type == 'sales':
            # Данные по продажам
            reports = SalesReport.objects.filter(
                date__range=[start_date, end_date],
                report_type='daily'
            ).order_by('date')

            data = {
                'labels': [r.date.strftime('%Y-%m-%d') for r in reports],
                'datasets': [{
                    'label': 'Продажи',
                    'data': [float(r.total_sales) for r in reports]
                }]
            }
        elif chart_type == 'categories':
            # Данные по категориям
            categories = CategoryPerformance.objects.filter(
                date__range=[start_date, end_date]
            ).values(
                'category__name'
            ).annotate(
                total_sales=Sum('total_sales')
            ).order_by('-total_sales')

            data = {
                'labels': [c['category__name'] for c in categories],
                'datasets': [{
                    'label': 'Продажи по категориям',
                    'data': [float(c['total_sales']) for c in categories]
                }]
            }
        else:
            data = {}

        serializer = ChartDataSerializer(data)
        return Response(serializer.data)