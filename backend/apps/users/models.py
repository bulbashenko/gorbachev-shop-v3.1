from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, validate_email
from django.core.exceptions import ValidationError
import uuid

def get_default_marketing_preferences():
    return {
        'email_notifications': True,
        'sms_notifications': False,
        'promotional_emails': True,
        'newsletter': True,
        'special_offers': True,
        'product_updates': True,
        'order_updates': True
    }

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        
        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email address')
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')
        
    # Basic fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # Personal information
    first_name = models.CharField(_('First name'), max_length=150)
    last_name = models.CharField(_('Last name'), max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True
    )

    # Address information
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

    # Status and security
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Verification fields
    email_verification_token = models.CharField(max_length=255, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    phone_verification_code = models.CharField(max_length=6, blank=True)
    phone_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Password reset fields
    password_reset_token = models.CharField(max_length=255, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Shop preferences
    newsletter_subscription = models.BooleanField(default=False)
    marketing_preferences = models.JSONField(
        default=get_default_marketing_preferences,
        help_text=_('User marketing preferences as JSON')
    )
    language_preference = models.CharField(max_length=10, default='en')
    currency_preference = models.CharField(max_length=3, default='USD')

    # Security metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['email_verified']),
            models.Index(fields=['is_active', 'is_verified']),
        ]

    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def clean(self):
        super().clean()
        if self.phone:
            self.phone = self.phone.strip().replace(' ', '')
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def record_login_attempt(self, success: bool, ip_address: str = None, device: str = None):
        """Record a login attempt and handle account locking"""
        if success:
            self.failed_login_attempts = 0
            self.last_login_ip = ip_address
            self.last_login_device = device
            self.account_locked_until = None
        else:
            self.failed_login_attempts += 1
            self.last_failed_login = timezone.now()
            
            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.account_locked_until = timezone.now() + timedelta(minutes=30)
                
        self.save(update_fields=[
            'failed_login_attempts', 'last_failed_login',
            'account_locked_until', 'last_login_ip',
            'last_login_device'
        ])

    def is_account_locked(self) -> bool:
        """Check if account is temporarily locked"""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False

    def send_verification_email(self):
        """Send email verification"""
        from apps.notifications.services import EmailService
        EmailService.send_verification_email(self)

    def send_password_reset_email(self):
        """Send password reset email"""
        from apps.notifications.services import EmailService
        EmailService.send_password_reset(self)

    def verify_email(self):
        """Verify email"""
        self.email_verified = True
        self.is_verified = True
        self.email_verification_token = ''
        self.save(update_fields=['email_verified', 'is_verified', 'email_verification_token'])

    def validate_verification_token(self, token: str, expiry_hours: int = 24) -> bool:
        """Validate verification token"""
        if self.email_verification_token != token:
            return False
            
        if self.email_verification_sent_at:
            token_age = timezone.now() - self.email_verification_sent_at
            if token_age > timedelta(hours=expiry_hours):
                return False
                
        return True

    def validate_reset_token(self, token: str, expiry_hours: int = 1) -> bool:
        """Validate password reset token"""
        if self.password_reset_token != token:
            return False
            
        if self.password_reset_sent_at:
            token_age = timezone.now() - self.password_reset_sent_at
            if token_age > timedelta(hours=expiry_hours):
                return False
                
        return True

    @property
    def has_valid_shipping_address(self) -> bool:
        """Check if user has valid shipping address"""
        return bool(self.default_shipping_address_id)

    @property
    def has_valid_billing_address(self) -> bool:
        """Check if user has valid billing address"""
        return bool(self.default_billing_address_id)

class UserAddress(models.Model):
    class AddressType(models.TextChoices):
        SHIPPING = 'shipping', _('Shipping')
        BILLING = 'billing', _('Billing')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.SHIPPING
    )
    is_default = models.BooleanField(default=False)
    
    # Address fields
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=17, validators=[User.phone_regex])
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=100, blank=True)
    
    # Additional information
    delivery_instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Address')
        verbose_name_plural = _('User Addresses')
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'address_type']),
            models.Index(fields=['is_default']),
            models.Index(fields=['country', 'city']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"

    def save(self, *args, **kwargs):
        # Clean fields
        self.full_name = self.full_name.strip()
        self.city = self.city.strip()
        self.street_address = self.street_address.strip()
        self.postal_code = self.postal_code.strip()
        
        if self.is_default:
            # Reset other default addresses of same type
            UserAddress.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
            
            # Update user's default address
            if self.address_type == self.AddressType.SHIPPING:
                self.user.default_shipping_address = self
            else:
                self.user.default_billing_address = self
            self.user.save(update_fields=[
                'default_shipping_address' if self.address_type == self.AddressType.SHIPPING 
                else 'default_billing_address'
            ])
            
        super().save(*args, **kwargs)

    @property
    def formatted_address(self) -> str:
        """Return formatted address string"""
        address_parts = [
            self.street_address,
            self.apartment,
            f"{self.city}, {self.state}" if self.state else self.city,
            self.postal_code,
            self.country
        ]
        return '\n'.join(filter(None, address_parts))
