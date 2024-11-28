from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from .category import CategoryAdmin
from .product import (
    ProductAdmin,
    ProductVariantAdmin,
    ProductImageAdmin,
    ProductAttributeAdmin
)
from .cart import CartAdmin, CartItemAdmin
from .order import OrderAdmin, OrderItemAdmin

# Customize admin site header and title
admin.site.site_header = _('Store Administration')
admin.site.site_title = _('Store Admin')
admin.site.index_title = _('Store Management')

__all__ = [
    'CategoryAdmin',
    'ProductAdmin',
    'ProductVariantAdmin',
    'ProductImageAdmin',
    'ProductAttributeAdmin',
    'CartAdmin',
    'CartItemAdmin',
    'OrderAdmin',
    'OrderItemAdmin',
]