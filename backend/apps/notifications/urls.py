from django.urls import path
from . import views

urlpatterns = [
    path('verify-email/<str:token>/', views.verify_email, name='verify-email'),
    path('password-reset/<str:token>/', views.reset_password, name='password-reset'),
]