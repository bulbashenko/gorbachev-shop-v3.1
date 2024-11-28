from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .base import BaseModel

class Category(BaseModel):
    """
    Category model for organizing products in a hierarchical structure.
    """
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'), blank=True)
    parent = models.ForeignKey(
        'self',
        verbose_name=_('Parent category'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_ancestors(self):
        """Get all parent categories up to the root."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors[::-1]

    def get_descendants(self):
        """Get all subcategories recursively."""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    @property
    def full_name(self):
        """Get the full category path name."""
        ancestors = self.get_ancestors()
        if ancestors:
            return " > ".join([cat.name for cat in ancestors] + [self.name])
        return self.name

    def clean(self):
        """Ensure a category cannot be its own parent or child."""
        if self.parent == self:
            raise ValidationError(_("A category cannot be its own parent."))
        if self.pk:
            if self in self.get_descendants():
                raise ValidationError(_("A category cannot be a parent of itself."))

    def save(self, *args, **kwargs):
        """Save the category with validation."""
        self.full_clean()
        super().save(*args, **kwargs)