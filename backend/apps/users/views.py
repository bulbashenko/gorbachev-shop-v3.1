from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import UserAddress
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserAddressSerializer,
    PasswordChangeSerializer
)

User = get_user_model()

@extend_schema(tags=['users'])
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'me']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()

    @extend_schema(
        summary="Get current user",
        description="Returns data of the currently authenticated user",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update current user",
        description="Updates the current user's information",
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Change password",
        description="Changes the current user's password",
        request=PasswordChangeSerializer,
        responses={200: None}
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Wrong password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'status': 'Password changed successfully'})

@extend_schema(tags=['addresses'])
class UserAddressViewSet(viewsets.ModelViewSet):
    """ViewSet для управления адресами пользователя."""
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Set default address",
        description="Sets the selected address as default for shipping or billing",
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                description="Address type (shipping/billing)",
                required=False,
                default="shipping"
            )
        ],
        responses={200: None}
    )
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        address_type = request.data.get('type', 'shipping')
        
        if address_type not in ['shipping', 'billing']:
            return Response(
                {'error': 'Invalid address type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if address_type == 'shipping':
            request.user.default_shipping_address = address
        else:
            request.user.default_billing_address = address
            
        request.user.save()
        return Response({'status': f'Default {address_type} address set successfully'})

@extend_schema(tags=['auth'])
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@extend_schema(tags=['auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Login to get tokens",
        description="Exchange credentials for JWT tokens",
        request=CustomTokenObtainPairSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {"$ref": "#/components/schemas/User"}
                }
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string"}
                }
            }
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@extend_schema(
    tags=['auth'],
    summary="Verify email",
    description="Verify user's email with token",
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.GET.get('token')
    
    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(
            email_verification_token=token,
            is_active=True
        )
        
        if user.email_verified:
            return Response(
                {'message': 'Email already verified'},
                status=status.HTTP_200_OK
            )
            
        if not user.validate_verification_token(token):
            return Response(
                {'error': 'Invalid or expired verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.verify_email()
        return Response({'message': 'Email verified successfully'})
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid verification token'},
            status=status.HTTP_400_BAD_REQUEST
        )

@extend_schema(
    tags=['auth'],
    summary="Request password reset",
    description="Request password reset email",
    request={"type": "object", "properties": {"email": {"type": "string", "format": "email"}}},
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    
    try:
        user = User.objects.get(email=email, is_active=True)
        user.send_password_reset_email()
        
        return Response({'message': 'Password reset email sent'})
        
    except User.DoesNotExist:
        # Для безопасности возвращаем тот же ответ
        return Response({'message': 'Password reset email sent'})

@extend_schema(
    tags=['auth'],
    summary="Reset password",
    description="Reset password using token",
    request={
        "type": "object",
        "properties": {
            "token": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ["token", "password"]
    },
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    token = request.data.get('token')
    new_password = request.data.get('password')
    
    try:
        validate_password(new_password)
    except ValidationError as e:
        return Response(
            {'error': e.messages},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(
            password_reset_token=token,
            is_active=True
        )
        
        if not user.validate_reset_token(token):
            return Response(
                {'error': 'Invalid or expired reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.password_reset_token = ''
        user.save()
        
        return Response({'message': 'Password reset successfully'})
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid reset token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
@extend_schema(
    tags=['auth'],
    summary="Resend verification email",
    description="Resends the verification email for the current user",
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification_email(request):
    user = request.user
    
    # Проверяем, не верифицирован ли уже email
    if user.email_verified:
        return Response(
            {'error': 'Email already verified'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Проверяем, не отправляли ли мы письмо недавно
    if user.email_verification_sent_at:
        time_since_last_email = timezone.now() - user.email_verification_sent_at
        if time_since_last_email < timedelta(minutes=5):  # Ограничение в 5 минут
            return Response(
                {'error': 'Please wait 5 minutes before requesting another verification email'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    user.send_verification_email()
    return Response({'message': 'Verification email sent successfully'})