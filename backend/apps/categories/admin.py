from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'parent',
        'slug',
        'is_active',
        'show_in_menu',
        'order',
        'created_at'
    )
    list_display_links = ('name',)
    list_filter = ('is_active', 'show_in_menu', 'parent')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Display Settings', {
            'fields': ('image', 'icon', 'is_active', 'show_in_menu', 'order')
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('created_at', 'updated_at')
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            # Exclude self from parent choices to prevent circular references
            if request.resolver_match.kwargs.get('object_id'):
                kwargs["queryset"] = Category.objects.exclude(
                    id=request.resolver_match.kwargs['object_id']
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)