from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic.edit import DeleteView

from accounts.models import Company
from core.mixins import LoginRequiredMixin
from .forms import ApplicantApplyForm, JobCreateForm
from .models import Applicant, Job

# Create your views here.


@login_required
def create(request, company_pk):
    user = request.user
    company = Company.objects.get(pk=company_pk)
    _is_company_collab = company.collaborators.filter(pk=user.pk).exists()

    if company.user == user or _is_company_collab:
        form = JobCreateForm(request.POST or None)

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

            messages.success(request, 'Your job has been created!')
            return HttpResponseRedirect(reverse(
                'jobs:detail',
                kwargs={'username': company.username, 'job_pk': new_job.pk}))

        context = {
            'company': company,
            'form': form
        }
        return render(request, 'jobs/create.html', context)
    return HttpResponseForbidden()


@login_required
def apply(request, job_pk):
    user = request.user
    job = Job.objects.get(pk=job_pk)

    if not user.gpa:
        messages.error(request, 'Please add your GPA first.')
        return redirect('accounts:account_settings')

    if not job.applicants.filter(pk=user.pk).exists():
        form = ApplicantApplyForm(request.POST or None,
                                  request.FILES or None,
                                  instance=user, user=user)

        if form.is_valid():
            _user_degree = '({})'.format(user.degree) if user.degree else ''
            applicant = Applicant.objects.create(
                user=user,
                resume=form.cleaned_data['resume'],
                name='{0} {1}'.format(user.first_name, user.last_name),
                email=form.cleaned_data['email'],
                university='{} {}'.format(user.university, _user_degree),
                cover_letter=form.cleaned_data['cover_letter']
            )
            job.applicants.add(applicant)

            # Send company an email with applicants information?

            messages.success(request, 'Thank you for applying!')
            return HttpResponseRedirect(reverse(
                'jobs:detail',
                kwargs={'username': job.company.username, 'job_pk': job_pk}))

        context = {
            'form': form,
            'job': job,
            'user': user
        }
        return render(request, 'jobs/apply.html', context)
    return HttpResponseForbidden()


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
