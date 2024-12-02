from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import uuid

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    description = models.TextField(_('Description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Parent category')
    )
    
    # Meta fields
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name=_('Category image')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class name (e.g. "fa fa-home")')
    )
    is_active = models.BooleanField(_('Active'), default=True)
    show_in_menu = models.BooleanField(_('Show in menu'), default=True)
    order = models.IntegerField(_('Order'), default=0)
    
    # SEO fields
    meta_title = models.CharField(
        _('Meta title'),
        max_length=255,
        blank=True
    )
    meta_description = models.TextField(
        _('Meta description'),
        blank=True
    )
    meta_keywords = models.CharField(
        _('Meta keywords'),
        max_length=255,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        """Returns the number of products in this category"""
        return self.products.count()

    def get_absolute_url(self):
        """Returns the URL for the category"""
        return f'/category/{self.slug}/'

    def get_children(self):
        """Returns all children categories"""
        return self.children.filter(is_active=True).order_by('order', 'name')

    def get_ancestors(self):
        """Returns all ancestor categories"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return reversed(ancestors)

    def get_descendants(self):
        """Returns all descendant categories"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants