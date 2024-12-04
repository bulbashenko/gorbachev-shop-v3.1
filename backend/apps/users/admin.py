from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserAddress

class UserAddressInline(admin.StackedInline):
    model = UserAddress
    extra = 0

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 
        'username', 
        'first_name', 
        'last_name',
        'is_active', 
        'is_verified', 
        'created_at', 
        'last_login'
    )
    list_filter = (
        'is_active', 
        'is_verified', 
        'is_staff',
        'email_verified', 
        'phone_verified',
        'newsletter_subscription', 
        'gender'
    )
    search_fields = (
        'email', 
        'username', 
        'first_name',
        'last_name', 
        'phone'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'last_login_ip', 
        'last_login'
    )
    inlines = [UserAddressInline]
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'username', 
                'first_name', 
                'last_name',
                'phone', 
                'birth_date', 
                'gender', 
                'avatar'
            )
        }),
        (_('Address Information'), {
            'fields': (
                'default_shipping_address',
                'default_billing_address'
            )
        }),
        (_('Verification & Security'), {
            'fields': (
                'is_verified', 
                'email_verified', 
                'phone_verified',
                'failed_login_attempts',
                'last_login_ip',
                'last_login_device'
            )
        }),
        (_('Preferences'), {
            'fields': (
                'newsletter_subscription',
                'marketing_preferences',
                'language_preference',
                'currency_preference'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined',
                'created_at',
                'updated_at'
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'username',
                'password1', 
                'password2',
                'first_name', 
                'last_name'
            ),
        }),
    )

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'address_type', 
        'full_name',
        'city', 
        'country', 
        'is_default', 
        'is_active'
    )
    list_filter = (
        'address_type', 
        'is_default', 
        'is_active', 
        'country'
    )
    search_fields = (
        'user__email', 
        'full_name', 
        'phone',
        'street_address', 
        'city', 
        'country'
    )
    readonly_fields = ('created_at', 'updated_at')