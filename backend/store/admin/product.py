from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Q, Count, Sum
from django.urls import reverse
from django.utils.safestring import mark_safe

from ..models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductAttribute,
    StockHistory
)
from .mixins import (
    ExportMixin,
    ActivationMixin,
    TimestampedAdminMixin,
    ImagePreviewMixin,
    StockManagementMixin
)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = [
        'sku',
        'attributes',
        'price_adjustment',
        'stock_quantity',
        'is_active'
    ]
    show_change_link = True


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = [
        'image',
        'alt_text',
        'type',
        'order',
        'image_preview'
    ]
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px;"/>',
                obj.image.url
            )
        return _("No image")


class StockHistoryInline(admin.TabularInline):
    model = StockHistory
    extra = 0
    fields = [
        'created_at',
        'user',
        'old_quantity',
        'new_quantity',
        'change_amount',
        'note'
    ]
    readonly_fields = [
        'created_at',
        'user',
        'old_quantity',
        'new_quantity',
        'change_amount',
        'note'
    ]
    ordering = ['-created_at']
    max_num = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(ExportMixin, ActivationMixin, TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'base_price',
        'is_active',
        'variant_count',
        'total_stock',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'category',
        'created_at'
    ]
    search_fields = [
        'name',
        'slug',
        'description',
        'variants__sku'
    ]
    prepopulated_fields = {
        'slug': ('name',)
    }
    inlines = [ProductVariantInline, ProductImageInline]
    actions = [
        'activate_items',
        'deactivate_items',
        'export_to_csv'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'category',
                'name',
                'slug',
                'description'
            )
        }),
        (_('Pricing'), {
            'fields': ('base_price',)
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Status and Timestamps'), {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'variants',
            'category'
        ).annotate(
            variants_count=Count('variants', filter=Q(variants__is_active=True)),
            total_stock_count=Sum('variants__stock_quantity')
        )

    def variant_count(self, obj):
        return getattr(obj, 'variants_count', obj.variants.count())
    variant_count.short_description = _('Variants')
    variant_count.admin_order_field = 'variants_count'

    def total_stock(self, obj):
        return getattr(obj, 'total_stock_count', 0) or 0
    total_stock.short_description = _('Total Stock')
    total_stock.admin_order_field = 'total_stock_count'

    def get_export_fields(self):
        return [
            'name',
            'category',
            'base_price',
            'total_stock',
            'is_active',
            'created_at'
        ]

    def get_category(self, obj):
        return obj.category.name

    class Media:
        css = {
            'all': ('admin/css/product.css',)
        }
        js = ('admin/js/product.js',)


@admin.register(ProductVariant)
class ProductVariantAdmin(StockManagementMixin, ActivationMixin, TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'sku',
        'product',
        'price_adjustment',
        'stock_quantity',
        'is_active',
        'final_price',
        'view_history'
    ]
    list_filter = [
        'is_active',
        'product__category',
        'created_at'
    ]
    search_fields = [
        'sku',
        'product__name',
        'attributes'
    ]
    raw_id_fields = ['product']
    inlines = [StockHistoryInline]
    actions = [
        'activate_items',
        'deactivate_items',
        'update_stock',
        'decrease_stock'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'product',
                'sku',
                'attributes',
                'price_adjustment',
                'stock_quantity'
            )
        }),
        (_('Status and Timestamps'), {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product',
            'product__category'
        )

    def final_price(self, obj):
        return obj.final_price
    final_price.short_description = _('Final Price')

    def view_history(self, obj):
        url = reverse('admin:store_stockhistory_changelist')
        return mark_safe(f'<a href="{url}?variant__id__exact={obj.pk}">{_("View History")}</a>')
    view_history.short_description = _('Stock History')

    def get_changelist_template(self, request):
        if request.path.endswith('/stock/'):
            return 'admin/store/product/stock_management.html'
        return super().get_changelist_template(request)

    class Media:
        css = {
            'all': ('admin/css/stock_management.css',)
        }
        js = ('admin/js/stock_management.js',)


@admin.register(ProductImage)
class ProductImageAdmin(ImagePreviewMixin, ActivationMixin, TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'product',
        'image_preview',
        'alt_text',
        'type',
        'order',
        'is_active'
    ]
    list_filter = [
        'type',
        'product',
        'is_active',
        'created_at'
    ]
    search_fields = [
        'product__name',
        'alt_text',
        'type'
    ]
    raw_id_fields = ['product', 'variant']
    ordering = ['product', 'order']
    actions = [
        'activate_items',
        'deactivate_items'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'product',
                'variant',
                'image',
                'alt_text',
                'type',
                'order'
            )
        }),
        (_('Preview'), {
            'fields': ('image_preview',)
        }),
        (_('Status and Timestamps'), {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['image_preview']


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'values_display'
    ]
    search_fields = ['name']

    def values_display(self, obj):
        return ", ".join(obj.values)
    values_display.short_description = _('Values')


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'variant',
        'created_at',
        'user',
        'old_quantity',
        'new_quantity',
        'change_amount',
        'note'
    ]
    list_filter = [
        'variant__product__category',
        'user',
        'created_at'
    ]
    search_fields = [
        'variant__sku',
        'variant__product__name',
        'user__username',
        'note'
    ]
    readonly_fields = [
        'variant',
        'user',
        'old_quantity',
        'new_quantity',
        'change_amount',
        'note',
        'created_at'
    ]
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {
            'all': ('admin/css/stock_history.css',)
        }