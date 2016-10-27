from __future__ import unicode_literals

import datetime

from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import Degree, MyUser, School
from activity.signals import activity_item

# Create your managers here.


class ApplicantManager(models.Manager):
    def create(self, user, resume, name, email, university, cover_letter='',
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
            .filter(
                Q(universities=user.undergrad_uni) |
                Q(universities=user.grad_uni),
                Q(degrees__pk__in=user.get_undergrad_degrees_pk) |
                Q(degrees__pk__in=user.get_grad_degrees_pk),
                list_date_start__lte=timezone.now(),
                list_date_end__gt=timezone.now(),
                min_gpa__lte=user.gpa,
                years__contains=user.year) \
            .distinct() \
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

    def create(self, user, company, title, contact_email, location,
               description, list_date_start, list_date_end,
               min_gpa=0.00, universities=School.objects.active(),
               years=",".join(str(year) for year in MyUser.YEAR_TYPES[0]),
               degrees=Degree.objects.active(),
               **extra_fields):
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
                         description=description,
                         list_date_start=start_date,
                         list_date_end=end_date,
                         min_gpa=min_gpa,
                         years=years,
                         **extra_fields)
        job.save(using=self._db)
        job.universities = universities
        job.degrees = degrees
        job.save(using=self._db)
        activity_item.send(
            company,
            verb='{} created a new job listing.'.format(user.get_full_name),
            target=job,
        )
        return job
