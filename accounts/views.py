from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import DeleteView

from core.mixins import LoginRequiredMixin
from jobs.models import Job
from .forms import (AccountSettingsForm, AddCollaboratorForm,
                    CompanySettingsForm, ExperienceForm)
from .models import Company, Experience, MyUser

# Create your views here.


@login_required
def exp_edit(request, exp_pk):
    user = request.user
    exp = Experience.objects.get(pk=exp_pk)

    if user != exp.user:
        return HttpResponseForbidden()

    form = ExperienceForm(request.POST or None,
                          instance=exp, user=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,
                         "You have successfully updated your experience.")
        return redirect(reverse(
            'profile', kwargs={"username": user.username}))

    context = {
        'form': form,
        'user': user
    }
    return render(request, 'accounts/exp_edit.html', context)


class ExpDelete(DeleteView, LoginRequiredMixin):
    model = Job
    success_message = "The experience was deleted."
    template_name = 'accounts/exp_delete.html'

    def get_object(self):
        user = self.request.user
        exp = Experience.objects.get(pk=self.kwargs['exp_pk'])
        if user != exp.user:
            raise HttpResponseForbidden()
        return exp

    def get_success_url(self):
        user = self.request.user
        return reverse_lazy('profile', kwargs={"username": user.username})

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object,
        deletes the experience, and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(success_url)


@login_required
@cache_page(60 * 3)
def profile(request, username):
    # User Profile
    try:
        user = MyUser.objects.get(username=username)

        if not user.is_active:
            raise Http404

        experiences = Experience.objects.own(user=user)
        form = ExperienceForm(request.POST or None,
                              instance=user, user=user)

        if request.method == 'POST':
            if form.is_valid():
                exp, created = Experience.objects.get_or_create(
                    user=user,
                    title=form.cleaned_data['title'],
                    company=form.cleaned_data['company'],
                    description=form.cleaned_data['description'],
                    date_start=form.cleaned_data['date_start'],
                    date_end=form.cleaned_data['date_end']
                )
                form.save()
                messages.success(request,
                                 "You have added an experience.")
            else:
                messages.error(request,
                               "There was an issue adding your experience.")

        context = {
            'experiences': experiences,
            'form': form,
            'user': user
        }
        template = 'accounts/profile.html'
    except MyUser.DoesNotExist:
        user = None

    # Company profile
    if not user:
        company = get_object_or_404(
            Company, Q(is_active=True), username=username)

        if not company.is_active:
            raise Http404

        _user_can_edit = False
        _is_company_collab = company.collaborators.filter(pk=request.user.pk)

        if company.user == request.user or _is_company_collab.exists():
            _user_can_edit = True

        jobs = Job.objects.own(company=company).filter(is_active=True)

        context = {
            'company': company,
            'jobs': jobs,
            'user_can_edit': _user_can_edit
        }
        template = 'accounts/company_public.html'
    return render(request, template, context)


@login_required
@cache_page(60)
def company_dash(request, username):
    user = request.user
    company = get_object_or_404(
        Company, Q(is_active=True), username=username)
    _is_company_collab = company.collaborators.filter(pk=user.pk).exists()

    if company.user == user or _is_company_collab:
        jobs = Job.objects.own(company=company)

        context = {
            'company': company,
            'jobs': jobs,
            'jobs_count': jobs.count,
            'active_job_count': jobs.filter(is_active=True).count(),
            'collaborator_count': company.collaborators.count() + 1,
            'collaborators': company.get_collaborators_info,
        }
        return render(request, 'accounts/company_dash.html', context)
    return HttpResponseForbidden()


@login_required
@never_cache
@sensitive_post_parameters()
def account_settings(request):
    user = get_object_or_404(MyUser, Q(is_active=True), pk=request.user.pk)
    form = AccountSettingsForm(request.POST or None,
                               request.FILES or None,
                               instance=user, user=user)

    if request.method == 'POST':

        if form.is_valid():
            form.email = form.cleaned_data['email']
            form.username = form.cleaned_data['username']
            form.video = form.cleaned_data['video']
            form.skills = form.cleaned_data['skills']
            password = form.cleaned_data['password_new_confirm']

            if password:
                current_user = form.user
                current_user.set_password(password)
                current_user.save()
                update_session_auth_hash(request, current_user)
            form.save()
            messages.success(request,
                             "You have successfully updated your profile.")
        else:
            messages.error(request, "There was an error.")
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'accounts/settings.html', context)


@login_required
@never_cache
def company_settings(request, username):
    user = request.user
    company = get_object_or_404(Company, Q(is_active=True), username=username)
    _is_company_collab = company.collaborators.filter(pk=user.pk).exists()

    if company.user == user or _is_company_collab:
        form = CompanySettingsForm(request.POST or None,
                                   request.FILES or None,
                                   instance=company, company=company)
        collab_form = AddCollaboratorForm(request.POST or None)

        if request.method == 'POST':

            if form.is_valid():
                form.username = form.cleaned_data['username']
                form.save()
                messages.success(
                    request,
                    "You have successfully updated your company.")

            if collab_form.is_valid():
                email = collab_form.cleaned_data['email']

                if email:
                    if not company.collaborators.filter(email__iexact=email).exists():
                        if MyUser.objects.filter(email__iexact=email).exists():
                            new_collab = MyUser.objects.get(email=email)
                            company.collaborators.add(new_collab)
                            messages.success(
                                request,
                                "That user has been added as a collaborator.")
                        else:
                            messages.error(
                                request,
                                "That user does not exist on this website.")
                    else:
                        messages.error(
                            request,
                            "That user is already a collaborator.")

        context = {
            'collab_form': collab_form,
            'company': company,
            'form': form,
            'initial_collaborators': company.get_collaborators_email,
        }
        return render(request, 'accounts/company_settings.html', context)
    raise Http404
