from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.utils import extend_schema
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductVariantViewSet,
    CartViewSet,
    OrderViewSet
)

app_name = 'store'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-variants', ProductVariantViewSet, basename='product-variant')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

# Define custom action patterns
urlpatterns = [
    path('cart/add-item/', 
         CartViewSet.as_view({'post': 'add_item'}), 
         name='cart-add-item'),
         
    path('cart/update-item/', 
         CartViewSet.as_view({'post': 'update_item'}), 
         name='cart-update-item'),
         
    path('cart/clear/', 
         CartViewSet.as_view({'post': 'clear'}), 
         name='cart-clear'),

    path('products/<slug:slug>/add-variant/', 
         ProductViewSet.as_view({'post': 'add_variant'}), 
         name='product-add-variant'),
         
    path('products/<slug:slug>/upload-images/', 
         ProductViewSet.as_view({'post': 'upload_images'}), 
         name='product-upload-images'),

    path('orders/<int:pk>/cancel/', 
         OrderViewSet.as_view({'post': 'cancel'}), 
         name='order-cancel'),

    path('', include(router.urls)),
]
