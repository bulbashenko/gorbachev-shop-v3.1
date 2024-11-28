from django.db import models
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    An abstract base class model that provides 'is_active' field
    and related manager methods.
    """
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        abstract = True

    @classmethod
    def active_objects(cls):
        return cls.objects.filter(is_active=True)


class LoggedModel(models.Model):
    """
    An abstract base class model that provides logging functionality
    for create and update operations.
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        model_name = self._meta.verbose_name.title()
        if is_new:
            logger.info(f"New {model_name} created: ID {self.pk}")
        else:
            logger.info(f"{model_name} updated: ID {self.pk}")


class BaseModel(TimeStampedModel, ActiveModel, LoggedModel):
    """
    A complete base abstract model that includes timestamps,
    active status, and logging functionality.
    """
    class Meta:
        abstract = True