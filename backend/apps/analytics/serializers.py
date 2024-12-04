from rest_framework import serializers
from .models import SalesReport, ProductPerformance, CategoryPerformance, CustomerSegment

class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = '__all__'

class ProductPerformanceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    category_name = serializers.CharField(source='product.category.name')
    
    class Meta:
        model = ProductPerformance
        fields = (
            'product_name', 'category_name', 'date',
            'units_sold', 'revenue', 'profit',
            'returns', 'return_rate', 'views',
            'unique_views', 'conversion_rate'
        )

class CategoryPerformanceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    
    class Meta:
        model = CategoryPerformance
        fields = (
            'category_name', 'date', 'total_sales',
            'total_orders', 'unique_customers',
            'average_order_value', 'total_returns',
            'return_rate', 'active_products',
            'out_of_stock_products'
        )

class CustomerSegmentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email')
    segment_description = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerSegment
        fields = (
            'user_email', 'recency_score', 'frequency_score',
            'monetary_score', 'total_spent', 'purchase_frequency',
            'days_since_last_purchase', 'is_churned',
            'churn_probability', 'segment_description'
        )

    def get_segment_description(self, obj):
        if obj.recency_score >= 4 and obj.frequency_score >= 4 and obj.monetary_score >= 4:
            return "Champions"
        elif obj.recency_score >= 3 and obj.frequency_score >= 3 and obj.monetary_score >= 3:
            return "Loyal Customers"
        elif obj.recency_score <= 2 and obj.frequency_score >= 3:
            return "At Risk"
        elif obj.recency_score <= 2 and obj.frequency_score <= 2:
            return "Lost"
        return "Regular"

class DashboardSerializer(serializers.Serializer):
    """Сериализатор для данных дашборда"""
    summary = serializers.DictField()
    sales_trend = serializers.ListField()
    top_products = serializers.ListField()
    category_distribution = serializers.ListField()
    rfm_distribution = serializers.DictField()

class ChartDataSerializer(serializers.Serializer):
    """Сериализатор для данных графиков"""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=serializers.DictField())