from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserAddress

User = get_user_model()

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'
        read_only_fields = ('user', 'id', 'created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    addresses = UserAddressSerializer(many=True, read_only=True)
    default_shipping_address = UserAddressSerializer(read_only=True)
    default_billing_address = UserAddressSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone', 'birth_date', 'gender', 'avatar',
            'is_verified', 'email_verified', 'phone_verified',
            'newsletter_subscription', 'marketing_preferences',
            'language_preference', 'currency_preference',
            'addresses', 'default_shipping_address', 'default_billing_address',
            'created_at', 'last_login'
        )
        read_only_fields = (
            'id', 'is_verified', 'email_verified', 'phone_verified',
            'created_at', 'last_login'
        )

class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей"""
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
    terms_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password2',
            'first_name', 'last_name', 'phone',
            'newsletter_subscription', 'terms_accepted'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        if not attrs.get('terms_accepted'):
            raise serializers.ValidationError({
                "terms_accepted": "You must accept the terms and conditions."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('terms_accepted')
        user = User.objects.create_user(**validated_data)
        return user

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Расширенный сериализатор для получения токенов"""
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Обновляем информацию о последнем входе
        user.last_login_ip = self.context['request'].META.get('REMOTE_ADDR')
        user.last_login_device = self.context['request'].META.get('HTTP_USER_AGENT', '')
        user.failed_login_attempts = 0
        user.save()

        # Добавляем пользовательские данные
        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'avatar': user.avatar.url if user.avatar else None,
            'email_verified': user.email_verified,
            'language_preference': user.language_preference,
            'currency_preference': user.currency_preference,
            'default_shipping_address': UserAddressSerializer(user.default_shipping_address).data if user.default_shipping_address else None,
            'default_billing_address': UserAddressSerializer(user.default_billing_address).data if user.default_billing_address else None,
        }
        data['token_type'] = 'Bearer'
        
        return data