from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic.edit import DeleteView

from accounts.models import Company, MyUser
from activity.models import Activity
from activity.signals import activity_item
from core.decorators import user_is_company_collab
from core.mixins import LoginRequiredMixin
from .forms import ApplicantApplyForm, JobCreateForm
from .models import Applicant, Job

# Create your views here.


@login_required
@user_is_company_collab
@cache_page(60 * 3)
def report(request, job_pk):
    job = get_object_or_404(Job, pk=job_pk)
    years = []

    for year in MyUser.YEAR_TYPES:
        if str(year[0]) in job.years:
            years.append(str(year[1]))

    context = {
        'applicants': job.applicants.all().prefetch_related('user'),
        'domain': request.get_host(),
        'highest_degrees': MyUser.DEGREE_TYPES,
        'job': job,
        'opp_sought': MyUser.OPPORTUNITY_TYPES,
        'protocol': 'https' if request.is_secure() else 'http',
        'years': years
    }
    return render(request, 'jobs/report.html', context)


@login_required
@user_is_company_collab
def create(request, company_pk):
    user = request.user
    company = Company.objects.get(pk=company_pk)
    form = JobCreateForm(request.POST or None,
                         initial={'contact_email': user.email})

    if form.is_valid():
        new_job = Job.objects.create(
            user=user,
            company=Company.objects.get(pk=company_pk),
            title=form.cleaned_data['title'],
            location=form.cleaned_data['location'],
            contact_email=form.cleaned_data['contact_email'],
            min_gpa=form.cleaned_data['min_gpa'],
            universities=form.cleaned_data['universities'],
            years=form.cleaned_data['years'],
            degrees=form.cleaned_data['degrees'],
            list_date_start=form.cleaned_data['list_date_start'],
            list_date_end=form.cleaned_data['list_date_end'],
            description=form.cleaned_data['description']
        )
        messages.success(request, 'Your job has been created!')
        return HttpResponseRedirect(new_job.get_absolute_url())

    context = {
        'company': company,
        'form': form
    }
    return render(request, 'jobs/create.html', context)


@login_required
def apply(request, job_pk):
    user = request.user
    job = Job.objects.get(pk=job_pk)

    if not user.gpa:
        messages.error(request, 'Please add your GPA first.')
        return redirect('accounts:account_settings')
    elif not user.undergrad_uni:
        messages.error(request, 'Please add your university first.')
        return redirect('accounts:account_settings')
    elif not user.undergrad_degree:
        messages.error(request, 'Please add your degree first.')
        return redirect('accounts:account_settings')
    elif not user.is_confirmed:
        messages.error(request, 'Please confirm your account before applying.')
        return redirect('/')

    if not job.applicants.filter(user__pk=user.pk).exists():
        form = ApplicantApplyForm(request.POST or None,
                                  request.FILES or None,
                                  instance=user, user=user)

        if form.is_valid():
            applicant = Applicant.objects.create(
                user=user,
                resume=form.cleaned_data['resume'],
                email=form.cleaned_data['email'],
                cover_letter=form.cleaned_data['cover_letter']
            )
            job.applicants.add(applicant)

            messages.success(request, 'Thank you for applying!')
            return HttpResponseRedirect(job.get_absolute_url())

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
    all_post_count = Job.objects.all().count()
    recent_posts = Job.objects.recent()[:7]
    _is_company_collab = job.company.collaborators.filter(pk=user.pk).exists()

    if job.company.user == user or _is_company_collab:
        viewer_can_delete = True

    context = {
        'all_post_count': all_post_count,
        'job': job,
        'recent_posts': recent_posts,
        'viewer_can_delete': viewer_can_delete,
        'viewer_has_applied': viewer_has_applied
    }
    return render(request, 'jobs/detail.html', context)


@login_required
@user_is_company_collab
def edit(request, username, job_pk):
    job = Job.objects.get(pk=job_pk)
    form = JobCreateForm(request.POST or None,
                         instance=job)

    if form.is_valid():
        form.save()
        activity_item.send(
            job.company,
            verb='{0} edited the {1} job listing.'.format(
                request.user.get_full_name, job.title),
            target=job,
        )
        messages.success(request,
                         'Your job listing has been updated!')
        return HttpResponseRedirect(job.get_absolute_url())

    context = {
        'form': form,
        'job': job
    }
    return render(request, 'jobs/edit.html', context)


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

    def _delete_activity(self):
        """
        Remove any previously set activity for the instance.
        """
        Activity.objects.filter(target_object_id=self.get_object().id).delete()

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object,
        deletes all applicants, and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        self._delete_applicants()  # Deletes applicants
        self._delete_activity()  # Deletes activity
        self.object.delete()  # Deletes the object
        activity_item.send(
            self.object.company,
            verb='{0} deleted the {1} job listing.'.format(
                request.user.get_full_name, self.object.title)
        )
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())
