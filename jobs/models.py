from __future__ import unicode_literals

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from accounts.models import Company
from core.models import TimeStampedModel
from .managers import ApplicantManager, JobManager

# Create your models here.


def get_resume_path(instance, filename):
    """
    Stores the resume in /applicant_resumes/username/filename.
    """
    return "/".join(['applicant_resumes', instance.user.username, filename])


@python_2_unicode_compatible
class Applicant(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    resume = models.FileField(upload_to=get_resume_path)
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120)
    university = models.CharField(max_length=200)
    cover_letter = models.TextField(max_length=1000, blank=True)

    objects = ApplicantManager()

    class Meta:
        app_label = 'jobs'
        verbose_name = _('applicant')
        verbose_name_plural = _('applicants')

    def __str__(self):
        return u'{0}'.format(self.user.get_full_name)

    def job_title(self):
        _job = Job.objects.get(applicants__pk=self.pk)
        return '{0} ({1})'.format(_job.title, _job.company.name)


@python_2_unicode_compatible
class Job(TimeStampedModel):
    company = models.ForeignKey(
        Company, related_name='job_owner', on_delete=models.CASCADE)
    applicants = models.ManyToManyField(
        Applicant, related_name='job_applicants', blank=True)
    title = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    contact_email = models.EmailField(max_length=120, null=True)
    description = models.TextField(max_length=5000)

    list_date_start = models.DateTimeField(_('Listing Start Date'), null=True)
    list_date_end = models.DateTimeField(_('Listing Expiration'), null=True)

    objects = JobManager()

    class Meta:
        app_label = 'jobs'
        verbose_name = _('job')
        verbose_name_plural = _('jobs')

    def __str__(self):
        return u'{0}'.format(self.title)

    def get_absolute_url(self):
        """
        Returns the url for the job.
        """
        return reverse('jobs:detail',
                       kwargs={"job_pk": self.pk,
                               "username": self.company.username})

    def get_edit_url(self):
        """
        Returns the edit url for the job.
        """
        return reverse('jobs:edit',
                       kwargs={"job_pk": self.pk,
                               "username": self.company.username})

    def get_delete_url(self):
        """
        Returns the delete url for the job.
        """
        return reverse('jobs:delete', kwargs={"job_pk": self.pk})

    def get_report_url(self):
        """
        Returns the report url for the job.
        """
        return reverse('jobs:report',
                       kwargs={"username": self.company.username,
                               "job_pk": self.pk})

    @cached_property
    def get_applicants_info(self):
        """
        Returns the information for each applicant as a list.
        """
        return self.applicants.values(
            'user__username', 'user__first_name', 'user__last_name',
            'user__profile_pic', 'user__email')

    @property
    def applicant_count(self):
        """
        Returns the number of applicants for the job.
        """
        return self.get_applicants_info.count()

    @cached_property
    def listing_start_date(self):
        """
        Returns the listing start date in the format:
        Month, day, year
        """
        return self.list_date_start.strftime("%B %d, %Y")

    @property
    def time_since(self):
        """
        Returns the time since the job has been posted.
        """
        return naturaltime(self.list_date_start)

    def is_active_job(self):
        start = self.list_date_start
        end = self.list_date_end
        return start <= timezone.now() and end >= timezone.now()
    is_active_job.boolean = True
