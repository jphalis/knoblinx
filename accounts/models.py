from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from tags.models import TagMixin
from .managers import (CompanyManager, ExperienceManager, MyUserManager,
                       SchoolManager)

# Create your models here.


def get_profile_pic_path(instance, filename):
    """
    Stores the profile picture in /profile_pictures/username/filename.
    """
    return "/".join(['profile_pictures', instance.username, filename])


def get_resume_path(instance, filename):
    """
    Stores the resume in /applicant_resumes/username/filename.
    """
    return "/".join(['resumes', instance.username, filename])


@python_2_unicode_compatible
class MyUser(AbstractBaseUser, PermissionsMixin, TagMixin):
    MALE = 0
    FEMALE = 1
    NO_ANSWER = 2
    GENDER_CHOICES = (
        (MALE, _('Male')),
        (FEMALE, _('Female')),
        (NO_ANSWER, _('Prefer not to answer')),
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=NO_ANSWER)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.SlugField(max_length=120, unique=True)
    email = models.EmailField(max_length=120, unique=True)
    profile_pic = models.ImageField(_('profile picture'),
                                    upload_to=get_profile_pic_path,
                                    null=True, blank=True)
    video = models.CharField(_('profile video'), max_length=250, blank=True,
                             help_text='Preferably embed from YouTube')
    resume = models.FileField(upload_to=get_resume_path, null=True, blank=True)
    university = models.CharField(max_length=180, blank=True)
    degree = models.CharField(max_length=120, blank=True)
    gpa = models.DecimalField(_('GPA'), max_digits=3, decimal_places=2,
                              null=True, blank=True)
    skills = models.CharField(max_length=250, blank=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    modified = models.DateTimeField(_('last modified'), auto_now=True)

    is_active = models.BooleanField(_('active'), default=True)
    is_confirmed = models.BooleanField(_('confirmed'), default=False)
    is_staff = models.BooleanField(_('staff'), default=False)

    tag_text_field = 'skills'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = MyUserManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_absolute_url(self):
        """
        Returns the url for the user.
        """
        return reverse('profile', kwargs={"username": self.username})

    @cached_property
    def get_full_name(self):
        """
        Returns the first_name plus the last_name.
        """
        return '{0} {1}'.format(self.first_name, self.last_name)

    @cached_property
    def get_short_name(self):
        """
        Returns the first name for the user.
        """
        return self.first_name

    @cached_property
    def gender_verbose(self):
        """
        Returns the verbose of the user's gender.
        """
        return dict(MyUser.GENDER_CHOICES)[self.gender]

    @property
    def user_profile_pic(self):
        """
        Returns the profile picture of a user.
        If there is no profile picture, a default one will be rendered.
        """
        if self.profile_pic:
            return "{0}{1}".format(settings.MEDIA_URL, self.profile_pic)
        return settings.STATIC_URL + 'img/default-profile-pic.jpg'

    @cached_property
    def skills_split(self):
        """
        Returns a comma-separated list of the user's skills.
        """
        return self.skills.split(',')

    @cached_property
    def skills_count(self):
        """
        Returns the number of skills the user has.
        """
        return self.skills_split.count()

    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        """
        return True

    def has_perm(self, perm, obj=None):
        """
        Does the user have a specific permission?
        """
        return True


def get_company_logo_path(instance, filename):
    """
    Stores the logo in /logos/username/filename.
    """
    return "/".join(['logos', instance.username, filename])


@python_2_unicode_compatible
class Company(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='company_owner',
                             null=True, on_delete=models.SET_NULL)
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='company_collaborators',
        blank=True)
    name = models.CharField(max_length=120)
    username = models.SlugField(max_length=150, unique=True)
    logo = models.ImageField(_('company logo'),
                             upload_to=get_company_logo_path,
                             null=True, blank=True)
    website = models.URLField(max_length=150, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    is_active = models.BooleanField(_('active'), default=True)

    objects = CompanyManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('company')
        verbose_name_plural = _('companies')

    def __str__(self):
        return u'{0}'.format(self.name)

    def get_absolute_url(self):
        """
        Returns the url for the company.
        """
        return reverse('profile', kwargs={"username": self.username})

    @property
    def company_logo(self):
        """
        Returns the logo of a company. If there is no logo,
        a default one will be rendered.
        """
        if self.logo:
            return "{0}{1}".format(settings.MEDIA_URL, self.logo)
        return settings.STATIC_URL + 'img/default-profile-pic.jpg'

    @cached_property
    def get_collaborators_info(self):
        """
        Returns the information for each collaborator as a list.
        """
        return self.collaborators.values(
            'username', 'first_name', 'last_name', 'profile_pic', 'email',)

    @cached_property
    def get_collaborators_email(self):
        """
        Returns the information for each collaborator as a list.
        """
        return self.collaborators.values_list('email', flat=True)

    @property
    def collaborators_count(self):
        """
        Returns the number of collaborators in the company.
        """
        return self.get_collaborators_info.count()


@python_2_unicode_compatible
class Experience(models.Model):
    user = models.ForeignKey(MyUser)
    title = models.CharField(max_length=120)
    company = models.CharField(max_length=120)
    description = models.TextField(max_length=500, blank=True)

    date_start = models.DateField(_('Start Date'), null=True)
    date_end = models.DateField(_('End State'), blank=True, null=True)

    objects = ExperienceManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('resume experience')
        verbose_name_plural = _('resume experiences')
        ordering = ['-date_end']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Returns the url for the experience.
        """
        return reverse('accounts:exp_edit', kwargs={"exp_pk": self.pk})

    @cached_property
    def experience_start_date(self):
        """
        Returns the start date in the format: MM/YYYY
        """
        return self.date_start.strftime("%m/%Y")

    @cached_property
    def experience_end_date(self):
        """
        Returns the end date in the format: MM/YYYY
        """
        if not self.date_end:
            return "present"
        return self.date_end.strftime("%m/%Y")


@python_2_unicode_compatible
class School(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)

    is_active = models.BooleanField(default=True)

    objects = SchoolManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = _('school')
        verbose_name_plural = _('schools')

    def __str__(self):
        return self.name
