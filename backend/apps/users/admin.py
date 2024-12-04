from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from .models import User, UserAddress, get_default_marketing_preferences

class UserAddressInline(admin.StackedInline):
    model = UserAddress
    extra = 0
    can_delete = True
    fields = (
        ('full_name', 'phone'),
        ('country', 'city'),
        'street_address',
        ('apartment', 'postal_code', 'state'),
        ('address_type', 'is_default'),
        'delivery_instructions',
        'is_active'
    )

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 
        'get_full_name', 
        'phone', 
        'account_status',
        'registration_date',
        'last_login',
        'get_orders_count'
    )
    list_filter = (
        'is_active', 
        'is_verified', 
        'is_staff',
        'email_verified', 
        'phone_verified',
        'groups',
        'created_at'
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
        'last_login',
        'account_status_details',
        'get_orders_summary',
        'marketing_preferences_display'
    )
    inlines = [UserAddressInline]
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'account_status_details')
        }),
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
        (_('Verification & Security'), {
            'fields': (
                'is_verified', 
                'email_verified', 
                'phone_verified',
                'failed_login_attempts',
                'last_login_ip',
                'last_login_device',
                'account_locked_until'
            )
        }),
        (_('Preferences'), {
            'fields': (
                'newsletter_subscription',
                'marketing_preferences',
                'marketing_preferences_display',
                'language_preference',
                'currency_preference'
            )
        }),
        (_('Addresses'), {
            'fields': (
                'default_shipping_address',
                'default_billing_address'
            )
        }),
        (_('Orders Summary'), {
            'fields': ('get_orders_summary',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
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
                'last_name',
                'marketing_preferences',
                'is_staff',
                'is_superuser'
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj and 'marketing_preferences' in form.base_fields:
            form.base_fields['marketing_preferences'].initial = get_default_marketing_preferences()
            form.base_fields['marketing_preferences'].help_text = 'Default marketing preferences will be applied'
        return form

    def marketing_preferences_display(self, obj):
        """Display marketing preferences in a readable format"""
        if not obj.marketing_preferences:
            return "No preferences set"
        
        html = ['<table style="width: 100%; border-collapse: collapse;">']
        html.append('<tr><th style="text-align: left; padding: 8px;">Preference</th><th style="text-align: left; padding: 8px;">Status</th></tr>')
        
        for key, value in obj.marketing_preferences.items():
            status = '✅' if value else '❌'
            key_display = key.replace('_', ' ').title()
            html.append(f'<tr><td style="padding: 8px;">{key_display}</td><td style="padding: 8px;">{status}</td></tr>')
        
        html.append('</table>')
        return format_html(''.join(html))
    marketing_preferences_display.short_description = _('Marketing Preferences Overview')

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')
    get_full_name.admin_order_field = 'first_name'

    def account_status(self, obj):
        """Display account status with color coding"""
        if not obj.is_active:
            return format_html(
                '<span style="color: red;">Inactive</span>'
            )
        if obj.is_account_locked():
            return format_html(
                '<span style="color: orange;">Locked</span>'
            )
        if obj.email_verified:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
        return format_html(
            '<span style="color: blue;">Pending</span>'
        )
    account_status.short_description = _('Status')

    def account_status_details(self, obj):
        """Detailed account status information"""
        details = []
        if not obj.is_active:
            details.append('❌ Account is inactive')
        if obj.is_account_locked():
            details.append(
                f'🔒 Account locked until: {obj.account_locked_until.strftime("%Y-%m-%d %H:%M")}'
            )
        if obj.failed_login_attempts > 0:
            details.append(f'⚠️ Failed login attempts: {obj.failed_login_attempts}')
        if not obj.email_verified:
            details.append('📧 Email not verified')
        if obj.email_verified and obj.is_active and not obj.is_account_locked():
            details.append('✅ Account is active and verified')
            
        return format_html('<br>'.join(details))
    account_status_details.short_description = _('Account Status Details')

    def registration_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    registration_date.short_description = _('Registered')
    registration_date.admin_order_field = 'created_at'

    def get_orders_count(self, obj):
        """Display number of orders with link"""
        from apps.orders.models import Order
        count = Order.objects.filter(user=obj).count()
        if count:
            url = reverse('admin:orders_order_changelist') + f'?user__id={obj.id}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return '0 orders'
    get_orders_count.short_description = _('Orders')

    def get_orders_summary(self, obj):
        """Display summary of user's orders"""
        from apps.orders.models import Order
        from django.db.models import Sum, Count
        
        orders = Order.objects.filter(user=obj)
        completed_orders = orders.filter(status='delivered')
        
        summary = orders.aggregate(
            total_spent=Sum('total'),
            total_orders=Count('id'),
            completed_orders=Count('id', filter={'status': 'delivered'}),
            cancelled_orders=Count('id', filter={'status': 'cancelled'})
        )
        
        if not summary['total_orders']:
            return 'No orders yet'
            
        avg_order_value = (
            summary['total_spent'] / summary['completed_orders']
            if summary['completed_orders'] else 0
        )
        
        return format_html(
            '''
            <strong>Total Orders:</strong> {}<br>
            <strong>Completed Orders:</strong> {}<br>
            <strong>Cancelled Orders:</strong> {}<br>
            <strong>Total Spent:</strong> ${:.2f}<br>
            <strong>Average Order Value:</strong> ${:.2f}
            ''',
            summary['total_orders'],
            summary['completed_orders'],
            summary['cancelled_orders'],
            summary['total_spent'] or 0,
            avg_order_value or 0
        )
    get_orders_summary.short_description = _('Orders Summary')

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        'user_link',
        'address_type',
        'full_name',
        'city',
        'country',
        'is_default',
        'is_active',
        'created_at'
    )
    list_filter = (
        'address_type',
        'is_default',
        'is_active',
        'country',
        'city',
        'created_at'
    )
    search_fields = (
        'user__email',
        'full_name',
        'phone',
        'street_address',
        'city',
        'country'
    )
    readonly_fields = ('created_at', 'updated_at', 'formatted_address')
    raw_id_fields = ('user',)
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'full_name', 'phone')
        }),
        (_('Address Information'), {
            'fields': (
                'country',
                'city',
                'street_address',
                'apartment',
                'postal_code',
                'state',
                'formatted_address'
            )
        }),
        (_('Settings'), {
            'fields': (
                'address_type',
                'is_default',
                'is_active',
                'delivery_instructions'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def user_link(self, obj):
        """Display user with link to user admin"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.email
        )
    user_link.short_description = _('User')
    user_link.admin_order_field = 'user__email'
