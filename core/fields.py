from __future__ import unicode_literals

import pytz

from django.db import models


class TimeZoneField(models.CharField):
    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": "",
            "choices": list(zip(pytz.all_timezones, pytz.all_timezones)),
            "blank": True,
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
