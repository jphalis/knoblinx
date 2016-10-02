from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import DeleteView

from accounts.models import Company
from core.mixins import LoginRequiredMixin
from .forms import ApplicantApplyForm, JobCreateForm
from .models import Applicant, Job

# Create your views here.


@login_required
def create(request, company_pk):
    form = JobCreateForm(request.POST or None)
    company = Company.objects.get(pk=company_pk)

    if form.is_valid():
        # Create the new job.
        new_job = Job.objects.create(
            company=Company.objects.get(pk=company_pk),
            title=form.cleaned_data['title'],
            location=form.cleaned_data['location'],
            contact_email=form.cleaned_data['contact_email'],
            list_date_start=form.cleaned_data['list_date_start'],
            list_date_end=form.cleaned_data['list_date_end'],
            description=form.cleaned_data['description']
        )
        new_job.save()

        messages.success(request, 'Your job has been successfully created!')
        return HttpResponseRedirect(reverse(
            'jobs:detail',
            kwargs={'username': company.username, 'job_pk': new_job.pk}))

    context = {
        'company': company,
        'form': form
    }
    return render(request, 'jobs/create.html', context)


@login_required
def apply(request, job_pk):
    form = ApplicantApplyForm(request.POST or None)
    job = Job.objects.get(pk=job_pk)

    if form.is_valid():

        """
        1. Redirect to a review page for students to see
        how their application will appear to employers.
            - show link to settings page to edit information

        2. Apply for job
        """

        # Create the new applicant.
        new_applicant = Applicant.objects.create(
            user=request.user,
            resume=form.cleaned_data['resume'],
            cover_letter=form.cleaned_data['cover_letter']
        )
        new_applicant.save()

        # Add applicant to job applicants.
        job.applicants.add(new_applicant)

        # Send company an email with applicants information?

        messages.success(request, 'Thank you for applying!')
        return HttpResponseRedirect(reverse(
            'jobs:detail', kwargs={'job_pk': job_pk}))

    context = {
        'form': form,
        'job': job
    }
    return render(request, 'jobs/apply.html', context)


@login_required
@cache_page(60 * 3)
def detail(request, job_pk, username):
    user = request.user
    job = get_object_or_404(Job, pk=job_pk)
    viewer_has_applied = job.applicants.filter(user=request.user).exists()
    viewer_can_delete = False
    recent_posts = Job.objects.recent()[:7]
    _is_company_collab = job.company.collaborators.filter(pk=user.pk).exists()

    if job.company.user == user or _is_company_collab:
        viewer_can_delete = True

    context = {
        'viewer_can_delete': viewer_can_delete,
        'viewer_has_applied': viewer_has_applied,
        'job': job,
        'recent_posts': recent_posts,
    }
    return render(request, 'jobs/detail.html', context)


@login_required
def edit(request, username, job_pk):
    user = request.user
    job = Job.objects.get(pk=job_pk)
    form = JobCreateForm(request.POST or None,
                         instance=job)
    company = Company.objects.get(username=username)
    _is_company_collab = company.collaborators.filter(pk=user.pk).exists()

    if company.user == user or _is_company_collab:
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Your job has been successfully created!')
            return HttpResponseRedirect(reverse(
                'jobs:detail',
                kwargs={'job_pk': job.pk, 'username': company.username}))

        context = {
            'company': company,
            'form': form
        }
        return render(request, 'jobs/edit.html', context)
    return HttpResponseForbidden()


@login_required
@require_http_methods(['POST'])
def job_active_ajax(request):
    job_pk = request.POST.get('job_pk')
    job = get_object_or_404(Job, pk=job_pk)
    if job.is_active:
        job_active = False
    else:
        job_active = True
    job.save()
    return JsonResponse({'job_active': job_active})


class Delete(DeleteView, LoginRequiredMixin):
    model = Job
    success_url = reverse_lazy('home')
    success_message = "The job has been deleted."
    template_name = 'jobs/delete.html'

    def get_object(self):
        user = self.request.user
        job = Job.objects.get(pk=self.kwargs['job_pk'])
        _is_company_collab = job.company.collaborators.filter(pk=user.pk)

        if job.company.user == user or _is_company_collab.exists():
            return job
        raise HttpResponseForbidden()

    def _delete_applicants(self):
        """
        Remove any previously set applicants for the instance.
        """
        self.object = self.get_object()
        self.object.applicants.clear()
        self.object.applicants.all().delete()

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object,
        deletes all applicants, and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self._delete_applicants()
        self.object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)
