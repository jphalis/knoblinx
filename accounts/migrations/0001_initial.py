# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-20 09:48
from __future__ import unicode_literals

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('gender', models.IntegerField(choices=[(0, 'Male'), (1, 'Female'), (2, 'Prefer not to answer')], default=2)),
                ('account_type', models.IntegerField(blank=True, choices=[(3, 'Student'), (4, 'Employer')], null=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('username', models.SlugField(max_length=120, unique=True)),
                ('email', models.EmailField(max_length=120, unique=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_profile_pic_path, verbose_name='profile picture')),
                ('video', models.CharField(blank=True, help_text='Preferably embed from YouTube', max_length=250, verbose_name='profile video')),
                ('resume', models.FileField(blank=True, null=True, upload_to=accounts.models.get_resume_path)),
                ('degree', models.CharField(blank=True, max_length=120)),
                ('gpa', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='GPA')),
                ('skills', models.CharField(blank=True, max_length=250)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('is_confirmed', models.BooleanField(default=False, verbose_name='confirmed')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('tags', models.ManyToManyField(blank=True, to='tags.Tag')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)),
                ('username', models.SlugField(max_length=150, unique=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_company_logo_path, verbose_name='company logo')),
                ('website', models.URLField(blank=True, max_length=150, null=True)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('collaborators', models.ManyToManyField(blank=True, related_name='company_collaborators', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'company',
                'verbose_name_plural': 'companies',
            },
        ),
        migrations.CreateModel(
            name='EmailConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_date', models.DateTimeField(auto_now_add=True)),
                ('key', models.CharField(max_length=64, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'email confirmation',
                'verbose_name_plural': 'email confirmations',
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('company', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True, max_length=500)),
                ('date_start', models.DateField(null=True, verbose_name='Start Date')),
                ('date_end', models.DateField(blank=True, null=True, verbose_name='End State')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_end'],
                'verbose_name': 'resume experience',
                'verbose_name_plural': 'resume experiences',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('location', models.CharField(blank=True, max_length=120)),
                ('email', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'school',
                'verbose_name_plural': 'schools',
            },
        ),
        migrations.AddField(
            model_name='myuser',
            name='university',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.School'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
