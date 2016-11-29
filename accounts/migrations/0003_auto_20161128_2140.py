# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-28 21:40
from __future__ import unicode_literals

import accounts.models
import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20161116_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='resume',
            field=models.FileField(blank=True, null=True, upload_to=accounts.models.get_resume_path, validators=[core.validators.validate_resume_ext]),
        ),
    ]
