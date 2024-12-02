from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_email(request, token):
    try:
        user = User.objects.get(
            email_verification_token=token,
            email_verified=False,
            is_active=True
        )
        
        # Проверяем срок действия токена
        if user.email_verification_sent_at:
            token_age = timezone.now() - user.email_verification_sent_at
            if token_age.days > 1:  # 24 часа
                messages.error(request, 'Verification link has expired')
                return redirect('login')
        
        user.verify_email()
        messages.success(request, 'Email verified successfully')
        return redirect('login')
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link')
        return redirect('login')