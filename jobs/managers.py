from __future__ import unicode_literals

import datetime

from django.db import models
from django.db.models import Count
from django.utils import timezone

# Create your managers here.


class ApplicantManager(models.Manager):
    def create(self, user, resume, cover_letter=None,
               **extra_fields):
        """
        Creates an applicant.
        """
        if not user:
            raise ValueError('There must be a user assigned to this object.')
        elif not resume:
            raise ValueError('Applicants must include their resume.')

        applicant = self.model(user=user,
                               resume=resume,
                               cover_letter=cover_letter,
                               **extra_fields)
        applicant.save(using=self._db)
        return applicant


class JobManager(models.Manager):
    def active(self):
        """
        Returns all active jobs.
        """
        return super(JobManager, self).get_queryset() \
            .filter(is_active=True) \
            .select_related('company') \
            .prefetch_related('applicants')

    def trending(self):
        """
        Returns all jobs with 10 or more applicants.
        """
        return super(JobManager, self).get_queryset() \
            .filter(is_active=True) \
            .annotate(the_count=(Count('applicants'))) \
            .filter(the_count__gte=10) \
            .order_by('-the_count')

    def recent(self):
        """
        Returns all recent jobs.
        """
        return super(JobManager, self).get_queryset() \
            .filter(is_active=True) \
            .order_by('-list_date_start')

    def own(self, company):
        """
        Returns all of the jobs for the company.
        """
        return super(JobManager, self).get_queryset() \
            .filter(company=company) \
            .select_related('company') \
            .prefetch_related('applicants') \
            .order_by('list_date_end')

    def user_applied(self, user):
        """
        Returns all of the jobs the user has applied to.
        """
        return super(JobManager, self).get_queryset() \
            .filter(applicants=user) \
            .prefetch_related('applicants') \
            .order_by('-applicants__created')

    def create(self, company, title, contact_email, location,
               list_date_start, list_date_end, description='', **extra_fields):
        """
        Creates a job posting with a default list date of now
        and removal date of 21 days later.
        """
        if not company:
            raise ValueError('There must be a company assigned to this job.')
        elif not title:
            raise ValueError('This job posting must have a title.')
        elif not description:
            raise ValueError('This job posting must have a description.')

        start_date = timezone.now()
        end_date = start_date + datetime.timedelta(days=21),

        if list_date_start:
            start_date = list_date_start
        if list_date_end:
            end_date = list_date_end

        job = self.model(company=company,
                         title=title,
                         contact_email=contact_email,
                         location=location,
                         list_date_start=start_date,
                         list_date_end=end_date,
                         description=description,
                         is_active=timezone.now() >= start_date,
                         **extra_fields)
        job.save(using=self._db)
        return job
