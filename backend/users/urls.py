from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', 
         RegisterView.as_view(), 
         name='register'),
    
    path('token/', 
         TokenObtainPairView.as_view(), 
         name='token_obtain'),
         
    path('token/refresh/', 
         TokenRefreshView.as_view(), 
         name='token_refresh'),
    
    # Profile endpoints
    path('profile/', 
         UserProfileView.as_view({
             'get': 'retrieve'
         }), 
         name='profile'),
         
    path('profile/update/', 
         UserProfileView.as_view({
             'put': 'update',
             'patch': 'partial_update'
         }), 
         name='profile_update'),
]