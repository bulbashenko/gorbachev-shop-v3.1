from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Сама схема API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI
    path('swagger/', 
         SpectacularSwaggerView.as_view(url_name='schema'), 
         name='swagger-ui'),
    
    # Redoc UI
    path('redoc/', 
         SpectacularRedocView.as_view(url_name='schema'), 
         name='redoc'),
]