from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from .models import User

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'phone', 'date_of_birth')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_password(self, value):
        """Validate password using Django's password validation."""
        try:
            # Validate password against all validators
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Additional validation for the entire data set."""
        # Ensure required fields are present
        if not attrs.get('email'):
            raise serializers.ValidationError({'email': 'Email is required'})
        if not attrs.get('username'):
            raise serializers.ValidationError({'username': 'Username is required'})
        
        # Validate password
        password = attrs.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as e:
                raise serializers.ValidationError({'password': list(e.messages)})
        else:
            raise serializers.ValidationError({'password': 'Password is required'})
        
        return attrs

    def create(self, validated_data):
        """Create a new user with validated data."""
        try:
            user = User.objects.create_user(
                email=validated_data['email'],
                username=validated_data['username'],
                password=validated_data['password'],
                phone=validated_data.get('phone', ''),
                date_of_birth=validated_data.get('date_of_birth', None)
            )
            return user
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone', 'date_of_birth', 'is_verified')
        read_only_fields = ('is_verified',)