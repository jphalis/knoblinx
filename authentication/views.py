from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from accounts.forms import AccountSettingsForm
from accounts.models import Company, MyUser, School
from .forms import (CompanySignupForm, LoginForm, SignupForm,
                    PasswordResetForm, PasswordResetTokenForm)
from .models import EmailConfirmation

# Create your views here.


def send_confirmation(request):
    EmailConfirmation.objects.send_confirmation(user=request.user,
                                                request=request)
    messages.success(request, 'The confirmation email has been sent.')
    return redirect('home')


def auth_logout(request):
    logout(request)
    return redirect('home')


@never_cache
def auth_login_register(request):
    if request.user.is_authenticated():
        return HttpResponseForbidden()

    next_url = request.GET.get('next', '/')

    # Login form
    login_form = LoginForm(request.POST or None)

    if login_form.is_valid() and 'login_form' in request.POST:
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password']
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.POST.get('next', 'home'))
        else:
            messages.warning(request, 'Username or password is incorrect.')

    # Registration form
    register_form = SignupForm(request.POST or None)

    if register_form.is_valid() and 'register_form' in request.POST:
        email = register_form.cleaned_data['email']
        password = register_form.cleaned_data['password_confirm']
        new_user = MyUser.objects.create_user(
            email=email,
            first_name=register_form.cleaned_data['first_name'],
            last_name=register_form.cleaned_data['last_name']
        )
        new_user.set_password(password)
        new_user.save()
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)

            # Confirmation email
            EmailConfirmation.objects.send_confirmation(user=user,
                                                        request=request)
            messages.success(request,
                             'Thank you for registering! '
                             'Please check your email to confirm '
                             'your account.')

            uni_emails = School.objects.active().values_list('email',
                                                             flat=True)
            username, domain = email.split('@')

            if not domain.endswith(tuple(uni_emails)):
                messages.error(request,
                               'Sorry, that school is not registered with us.')
            return redirect(request.POST.get('next', 'home'))

    context = {
        'login_form': login_form,
        'next': next_url,
        'register_form': register_form,
    }
    return render(request, 'auth/auth_login_register.html', context)


@login_required
def company_register(request):
    user = request.user

    if not user.is_confirmed:
        return HttpResponseForbidden()

    if Company.objects.filter(user=user).exists():
        return HttpResponseForbidden()

    form = CompanySignupForm(request.POST or None,
                             request.FILES or None)

    if form.is_valid():
        new_company = Company.objects.create(
            user=user,
            name=form.cleaned_data['name'],
            logo=form.cleaned_data['logo'],
            website=form.cleaned_data['website'],
            bio=form.cleaned_data['bio'],
        )
        new_company.save()
        user.account_type = MyUser.EMPLOYER
        user.save(update_fields=['account_type'])
        return redirect(reverse(
            'profile', kwargs={"username": new_company.username}))
    return render(request, 'auth/company_register.html', {'form': form})


@login_required
def student_register(request):
    user = get_object_or_404(MyUser, Q(is_active=True), pk=request.user.pk)

    if not user.is_confirmed:
        return HttpResponseForbidden()

    form = AccountSettingsForm(request.POST or None,
                               request.FILES or None,
                               instance=user, user=user)

    if request.method == 'POST':

        if form.is_valid():
            form.resume = form.cleaned_data['resume']
            form.gpa = form.cleaned_data['gpa']
            form.profile_picture = form.cleaned_data['profile_picture']
            form.video = form.cleaned_data['video']
            form.hobbies = form.cleaned_data['hobbies']
            form.save()
            user.account_type = MyUser.STUDENT
            user.save(update_fields=['account_type'])
            return redirect(reverse(
                'profile', kwargs={"username": user.username}))
        else:
            messages.error(request, "There was an error.")

    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'auth/student_register.html', context)


@sensitive_post_parameters()
@never_cache
def account_confirm(request, uidb64=None, token=None,
                    token_generator=default_token_generator):
    assert uidb64 is not None and token is not None

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    validlink = False

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        confirm = EmailConfirmation.objects.confirm(user=user)

        if confirm:
            messages.success(request, "Thank you for confirming your account!")
            return redirect('home')
    messages.error(request, "Account confirmation unsuccessful")
    return render(request, 'auth/selection.html', {'validlink': validlink})


def password_reset(request, from_email=settings.DEFAULT_FROM_EMAIL,
                   template_name='auth/password_reset_form.html',
                   email_template_name='auth/password_reset_email.html',
                   subject_template_name='KnobLinx Reset Account Password',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   html_email_template_name='auth/password_reset_email.html'):
    if request.user.is_authenticated():
        return HttpResponseForbidden()
    else:
        if request.method == "POST":
            form = password_reset_form(request.POST)

            if form.is_valid():
                opts = {
                    'use_https': request.is_secure(),
                    'token_generator': token_generator,
                    'from_email': from_email,
                    'email_template_name': email_template_name,
                    'subject_template_name': subject_template_name,
                    'request': request,
                    'html_email_template_name': html_email_template_name,
                }
                form.save(**opts)

                messages.success(
                    request,
                    "If that email is registered to an account, "
                    "instructions for resetting your password "
                    "will be sent soon. Please make sure to check "
                    "your junk email/spam folder if you do not "
                    "receive an email.")
        else:
            form = password_reset_form()
        return render(request, template_name, {'form': form})


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           token_generator=default_token_generator):
    if request.user.is_authenticated():
        return HttpResponseForbidden()

    assert uidb64 is not None and token is not None

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        form = PasswordResetTokenForm(request.POST or None, user=user)

        if request.method == 'POST':

            if form.is_valid():
                form.save()
                messages.success(request, "Password reset successfully.")
                return redirect('home')
    else:
        validlink = False
        form = None
        messages.error(request, "Password reset unsuccessful")
    context = {
        'form': form,
        'validlink': validlink,
    }
    return render(request, 'auth/password_set.html', context)
