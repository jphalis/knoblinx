from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class TimeStampedModel(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class ActiveStatusModel(models.Model):
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        abstract = True
