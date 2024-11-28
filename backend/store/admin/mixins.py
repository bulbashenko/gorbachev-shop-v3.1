from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.utils.html import format_html
import csv
import json

class ExportMixin:
    """Mixin to add CSV export functionality to admin classes."""
    def get_export_fields(self):
        """Override this method to specify fields for export."""
        raise NotImplementedError("Subclasses must implement get_export_fields()")

    def get_export_filename(self):
        """Override this method to specify export filename."""
        return f"{self.model._meta.model_name}s.csv"

    def export_to_csv(self, request, queryset):
        meta = self.model._meta
        field_names = self.get_export_fields()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_export_filename()}"'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row_data = []
            for field in field_names:
                if hasattr(self, f'get_{field}'):
                    value = getattr(self, f'get_{field}')(obj)
                else:
                    value = getattr(obj, field)
                row_data.append(str(value))
            writer.writerow(row_data)

        return response
    export_to_csv.short_description = _("Export selected items to CSV")


class ActivationMixin:
    """Mixin to add activation/deactivation functionality."""
    def activate_items(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} items were successfully activated.'))
    activate_items.short_description = _("Activate selected items")

    def deactivate_items(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} items were successfully deactivated.'))
    deactivate_items.short_description = _("Deactivate selected items")


class TimestampedAdminMixin:
    """Mixin to add created_at and updated_at to readonly fields."""
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return list(readonly_fields) + ['created_at', 'updated_at']


class ImagePreviewMixin:
    """Mixin to add image preview functionality."""
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;"/>',
                obj.image.url
            )
        return _("No image")
    image_preview.short_description = _("Preview")


class StockManagementMixin:
    """Mixin for managing product stock."""
    change_list_template = 'admin/store/product/stock_management.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/update-stock/',
                self.admin_site.admin_view(self.update_stock_view),
                name='%s_%s_update_stock' % (self.model._meta.app_label, self.model._meta.model_name)
            ),
            path(
                'notify-low-stock/',
                self.admin_site.admin_view(self.notify_low_stock_view),
                name='%s_%s_notify_low_stock' % (self.model._meta.app_label, self.model._meta.model_name)
            ),
            path(
                'export/',
                self.admin_site.admin_view(self.export_stock_view),
                name='%s_%s_export' % (self.model._meta.app_label, self.model._meta.model_name)
            ),
        ]
        return custom_urls + urls

    def update_stock(self, request, queryset, amount=10):
        """Batch update stock for selected items."""
        for obj in queryset:
            obj.stock_quantity = max(0, obj.stock_quantity + amount)
            obj.save()
        self.message_user(
            request,
            _(f'Added {amount} units to {queryset.count()} items.')
        )
    update_stock.short_description = _("Add stock")

    def decrease_stock(self, request, queryset, amount=10):
        """Batch decrease stock for selected items."""
        for obj in queryset:
            obj.stock_quantity = max(0, obj.stock_quantity - amount)
            obj.save()
        self.message_user(
            request,
            _(f'Removed {amount} units from {queryset.count()} items.')
        )
    decrease_stock.short_description = _("Decrease stock")

    def update_stock_view(self, request, object_id):
        """Handle individual stock updates."""
        if request.method != 'POST':
            return JsonResponse({'error': _('Method not allowed')}, status=405)

        try:
            variant = self.model.objects.get(pk=object_id)
            data = json.loads(request.body)
            new_quantity = int(data.get('quantity', 0))
            
            if new_quantity < 0:
                return JsonResponse(
                    {'error': _('Stock quantity cannot be negative')},
                    status=400
                )

            variant.stock_quantity = new_quantity
            variant.save()

            return JsonResponse({
                'success': True,
                'message': _('Stock updated successfully'),
                'new_quantity': new_quantity
            })
        except self.model.DoesNotExist:
            return JsonResponse(
                {'error': _('Product variant not found')},
                status=404
            )
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse(
                {'error': _('Invalid quantity value')},
                status=400
            )

    def notify_low_stock_view(self, request):
        """Handle low stock notifications."""
        if request.method != 'POST':
            return JsonResponse({'error': _('Method not allowed')}, status=405)

        low_stock_items = self.model.objects.filter(
            is_active=True,
            stock_quantity__lte=5
        )

        # Here you would implement your notification logic
        # For example, sending emails or notifications to staff

        return JsonResponse({
            'success': True,
            'message': _('Low stock notifications sent'),
            'count': low_stock_items.count()
        })

    def export_stock_view(self, request):
        """Export stock report."""
        queryset = self.model.objects.filter(is_active=True)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            _('Product'),
            _('SKU'),
            _('Stock Quantity'),
            _('Category'),
            _('Status')
        ])

        for obj in queryset:
            writer.writerow([
                obj.product.name,
                obj.sku,
                obj.stock_quantity,
                obj.product.category.name,
                _('Low Stock') if obj.stock_quantity <= 5 else _('In Stock')
            ])

        return response

    def changelist_view(self, request, extra_context=None):
        """Add extra context for stock management template."""
        extra_context = extra_context or {}
        extra_context.update({
            'total_products': self.model.objects.filter(is_active=True).count(),
            'low_stock_count': self.model.objects.filter(
                is_active=True,
                stock_quantity__lte=5
            ).count(),
            'out_of_stock_count': self.model.objects.filter(
                is_active=True,
                stock_quantity=0
            ).count(),
        })
        return super().changelist_view(request, extra_context=extra_context)