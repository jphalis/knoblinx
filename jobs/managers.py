from __future__ import unicode_literals

import datetime

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from activity.signals import activity_item

# Create your managers here.


class ApplicantManager(models.Manager):
    def create(self, user, resume, name, email, university, cover_letter=None,
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
                               name=name,
                               email=email,
                               university=university,
                               cover_letter=cover_letter,
                               **extra_fields)
        applicant.save(using=self._db)
        return applicant


class JobManager(models.Manager):
    def qualified(self, user):
        """
        Returns all jobs the user is qualified for.
        """
        return super(JobManager, self).get_queryset() \
            .filter(Q(list_date_start__lte=timezone.now()) &
                    Q(list_date_end__gt=timezone.now()) &
                    Q(min_gpa__lte=user.gpa) &
                    Q(universities=user.university)) \
            .exclude(applicants__user=user) \
            .select_related('company')

    def active(self):
        """
        Returns all active jobs.
        """
        return super(JobManager, self).get_queryset() \
            .filter(Q(list_date_start__lte=timezone.now()) &
                    Q(list_date_end__gt=timezone.now())) \
            .select_related('company')

    def trending(self):
        """
        Returns all jobs with 10 or more applicants.
        """
        return super(JobManager, self).get_queryset() \
            .filter(Q(list_date_start__lte=timezone.now()) &
                    Q(list_date_end__gt=timezone.now())) \
            .annotate(the_count=(Count('applicants'))) \
            .filter(the_count__gte=10) \
            .order_by('-the_count')

    def recent(self):
        """
        Returns all recent jobs.
        """
        return super(JobManager, self).get_queryset() \
            .filter(Q(list_date_start__lte=timezone.now()) &
                    Q(list_date_end__gt=timezone.now())) \
            .select_related('company') \
            .order_by('-list_date_start')

    def own(self, company):
        """
        Returns all of the jobs for the company.
        """
        return super(JobManager, self).get_queryset() \
            .filter(company=company) \
            .select_related('company') \
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
               list_date_start, list_date_end, description='',
               min_gpa=0.00, universities='', **extra_fields):
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
                         min_gpa=min_gpa,
                         universities=universities,
                         location=location,
                         list_date_start=start_date,
                         list_date_end=end_date,
                         description=description,
                         **extra_fields)
        job.save(using=self._db)
        activity_item.send(
            company,
            verb='Created a new job listing.',
            target=job,
        )
        return job
