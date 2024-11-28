from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models import Category
from .mixins import ExportMixin, ActivationMixin, TimestampedAdminMixin

@admin.register(Category)
class CategoryAdmin(ExportMixin, ActivationMixin, TimestampedAdminMixin, admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'parent',
        'is_active',
        'product_count',
        'created_at',
    ]
    list_filter = [
        'is_active',
        'parent',
        'created_at',
    ]
    search_fields = [
        'name',
        'slug',
        'description',
    ]
    prepopulated_fields = {
        'slug': ('name',)
    }
    ordering = ['name']
    actions = [
        'activate_items',
        'deactivate_items',
        'export_to_csv',
    ]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        (_('Status and Timestamps'), {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        """Get the number of products in this category."""
        return obj.products.count()
    product_count.short_description = _('Products')

    def get_export_fields(self):
        """Specify fields for CSV export."""
        return [
            'name',
            'slug',
            'parent',
            'description',
            'is_active',
            'product_count',
            'created_at',
        ]

    def get_export_filename(self):
        """Specify export filename."""
        return "categories.csv"

    def get_parent(self, obj):
        """Get parent category name for export."""
        return obj.parent.name if obj.parent else ''

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize parent category choices to prevent self-reference."""
        if db_field.name == "parent":
            if request._obj is not None:
                # Exclude self and descendants from parent choices
                kwargs["queryset"] = Category.objects.exclude(
                    pk__in=[request._obj.pk] + 
                           [c.pk for c in request._obj.get_descendants()]
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """Store the current object in request for use in formfield_for_foreignkey."""
        request._obj = obj
        return super().get_form(request, obj, **kwargs)

    class Media:
        css = {
            'all': ('admin/css/category.css',)
        }
        js = ('admin/js/category.js',)