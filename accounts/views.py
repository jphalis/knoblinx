from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import DeleteView

from activity.signals import activity_item
from core.decorators import account_type_required
from core.mixins import LoginRequiredMixin
from jobs.models import Job
from .forms import (AccountEmployerSettingsForm, AccountSettingsForm,
                    AddCollaboratorForm, CompanySettingsForm, ExperienceForm)
from .models import Company, Experience, MyUser

# Create your views here.


@login_required
def exp_edit(request, exp_pk):
    user = request.user
    exp = Experience.objects.get(pk=exp_pk)

    if user != exp.user:
        return HttpResponseForbidden()

    form = ExperienceForm(request.POST or None, instance=exp, user=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,
                         "You have successfully updated your experience.")
        return redirect(user.get_absolute_url())

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
        _exp = Experience.objects.get(pk=self.kwargs['exp_pk'])
        if self.request.user != _exp.user:
            raise HttpResponseForbidden()
        return _exp

    def get_success_url(self):
        return reverse_lazy(self.request.user.get_absolute_url())

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
    try:
        # User Profile
        user = MyUser.objects.get(username=username)
        form = ExperienceForm(request.POST or None, instance=user, user=user)

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
            'experiences': Experience.objects.own(user=user),
            'form': form,
            'is_employer': user.account_type == MyUser.EMPLOYER,
            'user': user
        }
        template = 'accounts/profile.html'
    except MyUser.DoesNotExist:
        # Company profile
        company = get_object_or_404(
            Company, Q(is_active=True), username=username)
        _user_can_edit = False
        _is_company_collab = company.collaborators.filter(pk=request.user.pk)

        if company.user == request.user or _is_company_collab.exists():
            _user_can_edit = True

        jobs = Job.objects.own(company=company).filter(
            Q(list_date_start__lte=timezone.now()) &
            Q(list_date_end__gt=timezone.now())
        )

        context = {
            'company': company,
            'jobs': jobs,
            'user_can_edit': _user_can_edit
        }
        template = 'accounts/company_public.html'
    return render(request, template, context)


@login_required
@account_type_required
@never_cache
@sensitive_post_parameters()
def account_settings(request):
    user = get_object_or_404(MyUser, Q(is_active=True), pk=request.user.pk)

    if user.account_type == MyUser.STUDENT:  # Student account
        form = AccountSettingsForm(request.POST or None,
                                   request.FILES or None,
                                   instance=user, user=user)

        if request.method == 'POST':

            if form.is_valid():
                form.email = form.cleaned_data['email']
                form.username = form.cleaned_data['username']
                form.video = form.cleaned_data['video']
                form.undergrad_degree = form.cleaned_data['undergrad_degree']
                form.grad_degree = form.cleaned_data['grad_degree']
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
    else:  # Company account
        form = AccountEmployerSettingsForm(request.POST or None,
                                           instance=user, user=user)

        if request.method == 'POST':

            if form.is_valid():
                form.email = form.cleaned_data['email']
                form.username = form.cleaned_data['username']
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
        'is_employer': user.account_type == MyUser.EMPLOYER,
        'user': user
    }
    return render(request, 'accounts/settings.html', context)


@login_required
@require_http_methods(['POST'])
def remove_collab(request):
    company = get_object_or_404(Company, pk=request.POST.get('company_pk'))

    try:
        user = company.collaborators.get(pk=request.POST.get('user_pk'))
        company.collaborators.remove(user)
        user.account_type = None
        user.save(update_fields=['account_type'])
        activity_item.send(
            company,
            verb='Removed a collaborator.',
            target=user,
        )
    except ValueError:
        user = None
    return JsonResponse({})


@login_required
@never_cache
def company_settings(request, username):
    user = request.user
    company = get_object_or_404(Company, Q(is_active=True), username=username)
    _is_company_collab = company.collaborators.filter(pk=user.pk).exists()

    if (company.user == user or _is_company_collab and
            user.account_type == MyUser.EMPLOYER):

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
                    if not company.collaborators.filter(email__iexact=email):
                        new_collab = MyUser.objects.filter(email__iexact=email)

                        if new_collab:
                            company.collaborators.add(new_collab[0])
                            new_collab[0].account_type = MyUser.EMPLOYER
                            new_collab[0].save(update_fields=['account_type'])
                            activity_item.send(
                                company,
                                verb='Added a collaborator.',
                                target=new_collab[0],
                            )
                            messages.success(
                                request,
                                "User has been added as a collaborator."
                            )
                        else:
                            messages.error(
                                request,
                                "That user does not exist on this website."
                            )
                    else:
                        messages.error(
                            request,
                            "That user is already a collaborator."
                        )

        context = {
            'collab_form': collab_form,
            'company': company,
            'form': form
        }
        return render(request, 'accounts/company_settings.html', context)
    return HttpResponseForbidden()
