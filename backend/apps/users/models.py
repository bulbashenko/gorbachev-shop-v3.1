from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
        
    # Основные поля
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Личная информация
    first_name = models.CharField(_('First name'), max_length=150)
    last_name = models.CharField(_('Last name'), max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True
    )
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True)

    # Адресная информация
    default_shipping_address = models.ForeignKey(
        'UserAddress',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_default_user'
    )
    default_billing_address = models.ForeignKey(
        'UserAddress',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_default_user'
    )

    # Статус и безопасность
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    # Поля для верификации email
    email_verification_token = models.CharField(max_length=255, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Поля для сброса пароля
    password_reset_token = models.CharField(max_length=255, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Настройки магазина
    newsletter_subscription = models.BooleanField(default=False)
    marketing_preferences = models.BooleanField(default=False)
    language_preference = models.CharField(max_length=10, default='en')
    currency_preference = models.CharField(max_length=3, default='USD')

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def send_verification_email(self):
        from apps.notifications.services import EmailService
        # Не используем транзакцию внутри этого метода
        EmailService.send_verification_email(self)

    def send_password_reset_email(self):
        """Отправка письма для сброса пароля"""
        from apps.notifications.services import EmailService
        EmailService.send_password_reset(self)

    def verify_email(self):
        """Подтверждение email"""
        self.email_verified = True
        self.email_verification_token = ''
        self.save()

    def validate_verification_token(self, token, expiry_hours=24):
        """Проверка валидности токена"""
        if self.email_verification_token != token:
            return False
            
        if self.email_verification_sent_at:
            token_age = timezone.now() - self.email_verification_sent_at
            if token_age > timedelta(hours=expiry_hours):
                return False
                
        return True

    def validate_reset_token(self, token, expiry_hours=1):
        """Проверка валидности токена сброса пароля"""
        if self.password_reset_token != token:
            return False
            
        if self.password_reset_sent_at:
            token_age = timezone.now() - self.password_reset_sent_at
            if token_age > timedelta(hours=expiry_hours):
                return False
                
        return True

class UserAddress(models.Model):
    class AddressType(models.TextChoices):
        SHIPPING = 'shipping', _('Shipping')
        BILLING = 'billing', _('Billing')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.SHIPPING
    )
    is_default = models.BooleanField(default=False)
    
    # Адресные поля
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=17, validators=[User.phone_regex])
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    
    # Дополнительная информация
    delivery_instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Сброс других адресов по умолчанию того же типа
            UserAddress.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)