from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', 
         SpectacularAPIView.as_view(), 
         name='schema'),
         
    path('api/redoc/', 
         SpectacularRedocView.as_view(
             url_name='schema',
             permission_classes=[permissions.AllowAny]
         ), 
         name='redoc'),
         
    path('api/swagger/', 
         SpectacularSwaggerView.as_view(
             url_name='schema',
             permission_classes=[permissions.AllowAny]
         ), 
         name='swagger'),
    
    # API URLs
    path('api/auth/', include('users.urls')),
    path('api/store/', include('store.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)