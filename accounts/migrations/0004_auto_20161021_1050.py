# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-21 10:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20161021_1023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myuser',
            old_name='degree',
            new_name='undergrad_degree',
        ),
        migrations.RenameField(
            model_name='myuser',
            old_name='university',
            new_name='undergrad_uni',
        ),
    ]
