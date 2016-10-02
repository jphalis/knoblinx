from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.utils.text import slugify

from core.utils import gen_rand_username

# Create your managers here.


class MyUserManager(BaseUserManager):
    def _create_user(self, email, first_name, last_name, password,
                     is_confirmed, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password,
        and automatically generates a username.
        """
        now = timezone.now()

        if not email:
            raise ValueError('Users must have an email.')
        elif not first_name:
            raise ValueError('Users must have a first name.')
        elif not last_name:
            raise ValueError('Users must have a last name.')

        email = self.normalize_email(email)

        if first_name and last_name:
            potential_username = slugify(
                "{0} {1}".format(first_name, last_name))

            try:
                username_exists = self.model.objects.get(
                    username=potential_username).exists()
            except self.model.DoesNotExist:
                username_exists = None

            if username_exists:
                username = gen_rand_username()
            else:
                username = potential_username

        user = self.model(email=email,
                          first_name=first_name,
                          last_name=last_name,
                          username=username,
                          is_confirmed=is_confirmed,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, password=None,
                    **extra_fields):
        return self._create_user(email, first_name, last_name, password,
                                 is_confirmed=False, is_staff=False,
                                 is_superuser=False, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password,
                         **extra_fields):
        return self._create_user(email, first_name, last_name, password,
                                 is_confirmed=True, is_staff=True,
                                 is_superuser=True, **extra_fields)


class CompanyManager(models.Manager):
    def create(self, user, name, **extra_fields):
        username = None

        if not name:
            raise ValueError('Companies must have a name.')

        potential_username = slugify("{0}".format(name))

        try:
            check_company = self.model.objects.get(
                username=potential_username).exists()
        except self.model.DoesNotExist:
            check_company = None

        if not check_company:
            username = potential_username
        else:
            username = gen_rand_username(initial_text='company')

        company = self.model(user=user,
                             name=name,
                             username=username,
                             is_active=True,
                             **extra_fields)
        company.save()
        return company

    def active(self):
        """
        Returns all active companies.
        """
        return super(CompanyManager, self).get_queryset().filter(
            is_active=True)


class ExperienceManager(models.Manager):
    def own(self, user):
        """
        Returns all of the user's experiences.
        """
        return super(ExperienceManager, self).get_queryset().filter(
            user=user)


class SchoolManager(models.Manager):
    def active(self):
        """
        Returns all active schools.
        """
        return super(SchoolManager, self).get_queryset().filter(
            is_active=True)
