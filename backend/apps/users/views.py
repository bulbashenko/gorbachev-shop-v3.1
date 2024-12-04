from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from datetime import timedelta
import logging

from .models import UserAddress
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserAddressSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

logger = logging.getLogger(__name__)
User = get_user_model()

@extend_schema(tags=['users'])
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    serializer_class = UserSerializer
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'reset_password', 'verify_email']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="Get current user profile",
        description="Returns the profile of the currently authenticated user",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update current user profile",
        description="Updates the current user's profile information",
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Change password",
        description="Changes the current user's password",
        request=PasswordChangeSerializer,
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': _('Wrong password')},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Invalidate all existing tokens
        RefreshToken.for_user(user)
        
        return Response({'message': _('Password changed successfully')})

    @extend_schema(
        summary="Request password reset",
        description="Sends a password reset email to the user",
        request=PasswordResetRequestSerializer,
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def request_password_reset(self, request):
        """Request password reset email"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(
                email=serializer.validated_data['email'],
                is_active=True
            )
            user.send_password_reset_email()
            return Response({'message': _('Password reset email sent')})
        except User.DoesNotExist:
            # Return same response for security
            return Response({'message': _('Password reset email sent')})

    @extend_schema(
        summary="Reset password",
        description="Resets user password using token",
        request=PasswordResetConfirmSerializer,
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """Reset password with token"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(
                password_reset_token=serializer.validated_data['token'],
                is_active=True
            )
            
            if not user.validate_reset_token(serializer.validated_data['token']):
                return Response(
                    {'error': _('Invalid or expired reset token')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.password_reset_token = ''
            user.save()
            
            # Invalidate all existing tokens
            RefreshToken.for_user(user)
            
            return Response({'message': _('Password reset successfully')})
            
        except User.DoesNotExist:
            return Response(
                {'error': _('Invalid reset token')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Verify email",
        description="Verifies user email with token",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def verify_email(self, request):
        """Verify email with token"""
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {'error': _('Token is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(
                email_verification_token=token,
                is_active=True
            )
            
            if user.email_verified:
                return Response({'message': _('Email already verified')})
                
            if not user.validate_verification_token(token):
                return Response(
                    {'error': _('Invalid or expired verification token')},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            user.verify_email()
            return Response({'message': _('Email verified successfully')})
            
        except User.DoesNotExist:
            return Response(
                {'error': _('Invalid verification token')},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Resend verification email",
        description="Resends the verification email for the current user",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        """Resend verification email"""
        user = request.user
        
        if user.email_verified:
            return Response(
                {'error': _('Email already verified')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.email_verification_sent_at:
            time_since_last_email = timezone.now() - user.email_verification_sent_at
            if time_since_last_email < timedelta(minutes=5):
                return Response(
                    {'error': _('Please wait 5 minutes before requesting another verification email')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user.send_verification_email()
        return Response({'message': _('Verification email sent successfully')})

@extend_schema(tags=['users'])
class UserAddressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user addresses"""
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Set default address",
        description="Sets the selected address as default for shipping or billing",
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    )
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set address as default"""
        address = self.get_object()
        address_type = request.data.get('type', 'shipping')
        
        if address_type not in ['shipping', 'billing']:
            return Response(
                {'error': _('Invalid address type')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        address.is_default = True
        address.address_type = address_type
        address.save()
        
        return Response({
            'message': _(f'Default {address_type} address set successfully')
        })

@extend_schema(tags=['auth'])
class RegisterView(generics.CreateAPIView):
    """View for user registration"""
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = serializer.save()
            # Remove this line since the signal will handle sending the email
            # user.send_verification_email()
            
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {'error': _('Registration failed. Please try again.')},
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema(tags=['auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """Enhanced JWT token view with additional security"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Check if account is locked
        try:
            user = User.objects.get(email=request.data.get('email'))
            if user.is_account_locked():
                return Response(
                    {
                        'error': _('Account is temporarily locked. Please try again later.'),
                        'locked_until': user.account_locked_until
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            pass

        response = super().post(request, *args, **kwargs)
        
        # Record failed login attempt if necessary
        if response.status_code != status.HTTP_200_OK and 'email' in request.data:
            try:
                user = User.objects.get(email=request.data.get('email'))
                user.record_login_attempt(
                    success=False,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except User.DoesNotExist:
                pass
            
        return response