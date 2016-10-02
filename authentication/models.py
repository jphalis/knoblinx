from __future__ import unicode_literals

import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import EmailConfirmationManager

# Create your models here.


@python_2_unicode_compatible
class EmailConfirmation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    sent_date = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")

    def __str__(self):
        return "Confirmation for {0}".format(
            self.user.get_full_name)

    def key_valid(self):
        expiration_date = self.sent_date + datetime.timedelta(days=7)
        return expiration_date > timezone.now()
    key_valid.boolean = True
