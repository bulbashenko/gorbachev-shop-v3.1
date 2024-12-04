from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Gorbachev Shop Admin'
admin.site.site_title = 'Gorbachev Shop Admin Portal'
admin.site.index_title = 'Welcome to Gorbachev Shop Admin Portal'

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),
    
    # API documentation
    path('api/', include('docs.schema')),
    
    # App URLs
    path('api/users/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
