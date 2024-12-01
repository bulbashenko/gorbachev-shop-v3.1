from django_filters import rest_framework as filters
from django.db import models
from .models import Product, Size, Color

class ProductFilter(filters.FilterSet):
    # Поиск
    search = filters.CharFilter(method='search_filter')
    
    # Цена
    price_min = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="price", lookup_expr='lte')
    
    # Категории
    category = filters.NumberFilter(field_name="category")
    category_slug = filters.CharFilter(field_name="category__slug")
    
    # Характеристики
    sizes = filters.ModelMultipleChoiceFilter(
        field_name='variants__size',
        queryset=Size.objects.all(),
        distinct=True
    )
    colors = filters.ModelMultipleChoiceFilter(
        field_name='variants__color',
        queryset=Color.objects.all(),
        distinct=True
    )
    
    # Дополнительные фильтры
    gender = filters.ChoiceFilter(choices=Product.GENDER_CHOICES)
    brand = filters.CharFilter(lookup_expr='iexact')
    is_sale = filters.BooleanFilter(method='sale_filter')
    in_stock = filters.BooleanFilter(method='stock_filter')

    class Meta:
        model = Product
        fields = [
            'search', 'category', 'category_slug', 
            'price_min', 'price_max', 'sizes', 
            'colors', 'gender', 'brand', 
            'is_sale', 'in_stock'
        ]

    def search_filter(self, queryset, name, value):
        """Поиск по имени, описанию и бренду"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(brand__icontains=value)
        )

    def sale_filter(self, queryset, name, value):
        """Фильтр товаров со скидкой"""
        if value:
            return queryset.filter(sale_price__isnull=False)
        return queryset

    def stock_filter(self, queryset, name, value):
        """Фильтр товаров в наличии"""
        if value:
            return queryset.filter(variants__stock__gt=0).distinct()
        return queryset