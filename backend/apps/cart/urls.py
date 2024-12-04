from django.urls import path
from .views import CartViewSet

urlpatterns = [
    path('', CartViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('add_item/', CartViewSet.as_view({
        'post': 'add_item'
    })),
    path('remove_item/', CartViewSet.as_view({
        'delete': 'remove_item'
    })),
    path('update_quantity/', CartViewSet.as_view({
        'patch': 'update_quantity'
    })),
    path('clear/', CartViewSet.as_view({
        'post': 'clear'
    })),
    path('validate/', CartViewSet.as_view({
        'get': 'validate'
    })),
    path('transfer_to_user/', CartViewSet.as_view({
        'post': 'transfer_to_user'
    }))
]
