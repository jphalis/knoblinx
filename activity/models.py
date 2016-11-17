from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel

# Create your models here.


class ActivityManager(models.Manager):
    def own(self, company):
        """
        Returns all of the activity items the company has created.
        """
        return super(ActivityManager, self).get_queryset() \
            .filter(sender_object_id=company.id)


@python_2_unicode_compatible
class Activity(TimeStampedModel):
    sender_content_type = models.ForeignKey(ContentType,
                                            related_name='activity_sender')
    sender_object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey("sender_content_type",
                                      "sender_object_id")
    verb = models.CharField(max_length=255)

    action_content_type = models.ForeignKey(ContentType,
                                            related_name='activity_action',
                                            null=True, blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey("action_content_type",
                                      "action_object_id")

    target_content_type = models.ForeignKey(ContentType,
                                            related_name='activity_target',
                                            null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey("target_content_type",
                                      "target_object_id")

    objects = ActivityManager()

    class Meta:
        ordering = ['-created']
        app_label = 'activity'
        verbose_name = _('activity')
        verbose_name_plural = _('activities')

    def __str__(self):
        context = {
            # "action": self.action_object,
            "sender": self.sender_object,
            "target": self.target_object,
            "verb": self.verb,
        }
        return '{}'.format(context['verb'])

    @property
    def time_since(self):
        """
        Returns the time since the notification was created.
        """
        return naturaltime(self.created)

    def get_target_url(self):
        """
        Returns the target_url of the object.
        """
        return reverse('jobs:detail',
                       kwargs={'username': self.sender_object.username,
                               'job_pk': self.target_object_id})
