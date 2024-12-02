from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from . import views
from .views import (
    UserViewSet,
    UserAddressViewSet,
    RegisterView,
    CustomTokenObtainPairView,
    verify_email,
    request_password_reset,
    reset_password,
    resend_verification_email  # Добавляем новый view
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('addresses', UserAddressViewSet, basename='address')

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/verify-email/', verify_email, name='verify-email'),
    path('auth/resend-verification/', resend_verification_email, name='resend-verification'),  # Новый URL
    path('auth/request-password-reset/', request_password_reset, name='request-password-reset'),
    path('auth/reset-password/', reset_password, name='reset-password'),
    
    # Router URLs
    path('', include(router.urls)),
]