from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import UserAddress

User = get_user_model()

class UserAddressSerializer(serializers.ModelSerializer):
    formatted_address = serializers.CharField(read_only=True)

    class Meta:
        model = UserAddress
        fields = [
            'id', 'address_type', 'is_default', 'full_name',
            'phone', 'country', 'city', 'street_address',
            'apartment', 'postal_code', 'state',
            'delivery_instructions', 'formatted_address',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            value = value.strip().replace(' ', '')
            try:
                User.phone_regex(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
        return value

class UserSerializer(serializers.ModelSerializer):
    addresses = UserAddressSerializer(many=True, read_only=True)
    default_shipping_address = UserAddressSerializer(read_only=True)
    default_billing_address = UserAddressSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True, source='get_full_name')
    has_valid_shipping_address = serializers.BooleanField(read_only=True)
    has_valid_billing_address = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone', 'birth_date', 'gender', 'avatar',
            'is_verified', 'email_verified', 'phone_verified',
            'newsletter_subscription', 'marketing_preferences',
            'language_preference', 'currency_preference',
            'addresses', 'default_shipping_address',
            'default_billing_address', 'has_valid_shipping_address',
            'has_valid_billing_address', 'created_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'is_verified', 'email_verified',
            'phone_verified', 'created_at', 'last_login'
        ]

    def validate_phone(self, value):
        if value:
            value = value.strip().replace(' ', '')
            try:
                User.phone_regex(value)
            except ValidationError as e:
                raise serializers.ValidationError(str(e))
        return value

    def validate_marketing_preferences(self, value):
        """Validate marketing preferences structure"""
        required_keys = {'email', 'sms', 'push'}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Marketing preferences must be a dictionary")
        if not all(key in value for key in required_keys):
            raise serializers.ValidationError(
                f"Marketing preferences must contain all required keys: {required_keys}"
            )
        return value

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    terms_accepted = serializers.BooleanField(required=True, write_only=True)
    marketing_preferences = serializers.DictField(
        required=False,
        default=lambda: {'email': False, 'sms': False, 'push': False}
    )

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password2',
            'first_name', 'last_name', 'phone',
            'newsletter_subscription', 'marketing_preferences',
            'terms_accepted', 'language_preference',
            'currency_preference'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": _("Password fields didn't match.")
            })
        if not attrs['terms_accepted']:
            raise serializers.ValidationError({
                "terms_accepted": _("You must accept the terms and conditions.")
            })
        return attrs

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError(_("User with this email already exists."))
        return normalized_email

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('terms_accepted')
        user = User.objects.create_user(**validated_data)
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": _("Password fields didn't match.")
            })
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enhanced JWT token serializer with additional user info"""
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Record successful login attempt with IP and device info
        request = self.context.get('request')
        if request:
            user.record_login_attempt(
                success=True,
                ip_address=request.META.get('REMOTE_ADDR'),
                device=request.META.get('HTTP_USER_AGENT', '')
            )

        # Add custom data to response
        data.update({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'full_name': user.get_full_name(),
                'phone': user.phone,
                'avatar': user.avatar.url if user.avatar else None,
                'email_verified': user.email_verified,
                'language_preference': user.language_preference,
                'currency_preference': user.currency_preference,
                'has_valid_shipping_address': user.has_valid_shipping_address,
                'has_valid_billing_address': user.has_valid_billing_address,
            },
            'token_type': 'Bearer'
        })
        return data