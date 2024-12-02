from django.contrib import admin
from .models import Product, ProductVariant, ProductImage, Size, Color

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'brand', 'price',
        'sale_price', 'is_active', 'created_at'
    )
    list_filter = (
        'is_active', 'category', 'brand',
        'gender', 'created_at'
    )
    search_fields = ('name', 'description', 'brand')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'slug', 'description',
                'category', 'brand', 'gender'
            )
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Details', {
            'fields': ('material', 'care_instructions')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'sku', 'stock')
    list_filter = ('size', 'color', 'stock')
    search_fields = ('sku', 'product__name')
    raw_id_fields = ('product',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'is_main', 'order')
    list_filter = ('is_main', 'color')
    search_fields = ('product__name',)
    raw_id_fields = ('product',)