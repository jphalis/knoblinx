"""
Glossary of authentication/forms.py:

- Company creation form (admin only)
- Company signup form
- MyUser creation form (admin only)
- Login form
- Signup form
- Password reset form
- Password reset token form
"""

from __future__ import unicode_literals

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.forms.widgets import ClearableFileInput
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from accounts.models import Company, MyUser
from core.utils import clean_passwords

# Create your forms here.


class MyUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given
    fields.
    """
    def __init__(self, *args, **kargs):
        super(MyUserCreationForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'username',)

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        _value = self.cleaned_data['email'].lower()
        if self.initial.get('email') == _value:
            return _value
        if MyUser.objects.filter(email__iexact=_value).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return _value


class CompanyCreationForm(forms.ModelForm):
    """
    A form that creates a company profile in the admin.
    """
    class Meta:
        models = Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CompanyCreationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        _value = self.cleaned_data['username'].lower()
        if Company.objects.filter(username__iexact=_value).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return _value


class CompanySignupForm(forms.Form):
    name = forms.CharField(
        label=_('Company Name'),
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Name',
                   'name': 'name'}),
        max_length=120
    )
    logo = forms.ImageField(
        label=_('Company Logo'),
        widget=ClearableFileInput(
            attrs={'class': 'form-control',
                   'style': 'padding-top:30px;',
                   'name': 'logo'}),
        required=False
    )
    website = forms.URLField(
        widget=forms.URLInput(
            attrs={'name': 'website',
                   'placeholder': 'http://www.example.com'}),
        max_length=150,
        required=False
    )
    bio = forms.CharField(
        label=_('About'),
        widget=forms.Textarea(
            attrs={'placeholder': 'Tell us about your company.',
                   'name': 'bio'}),
        max_length=500,
        required=False
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        max_length=120
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'},
            render_value=False)
    )

    def clean_email(self):
        """
        Makes the value of the email lowercase, and verifies the
        account is not disabled.
        """
        _value = self.cleaned_data.get("email").lower()
        if MyUser.objects.filter(Q(email__iexact=_value) &
                                 Q(is_active=False)).exists():
            raise forms.ValidationError("This account has been disabled")
        return _value


class SignupForm(forms.Form):
    first_name = forms.CharField(
        label=_('First Name'),
        widget=forms.TextInput(attrs={'placeholder': 'First Name'},),
        max_length=50
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'},),
        max_length=50
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        max_length=120
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password'},
            render_value=False)
    )
    password_confirm = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password confirm'},
            render_value=False)
    )

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        _value = self.cleaned_data['email'].lower()
        if MyUser.objects.filter(email__iexact=_value).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return _value

    def clean_password_confirm(self):
        clean_passwords(data=self.cleaned_data,
                        password1="password",
                        password2="password_confirm")
        return self.cleaned_data['password_confirm']


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.widgets.EmailInput(attrs={'placeholder': 'Email'})
    )

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = subject_template_name
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body,
                                               from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name,
                                                 context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = MyUser._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, subject_template_name='KnobLinx Reset Password',
             email_template_name='accounts/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=settings.DEFAULT_HR_EMAIL, request=None,
             html_email_template_name='accounts/password_reset_email.html',
             extra_email_context=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"].lower()
        for user in self.get_users(email):
            context = {
                'email': user.email,
                'domain': request.get_host(),
                'site_name': request.META['SERVER_NAME'],
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)


class PasswordResetTokenForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password.
    """
    password_new = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False),
        required=False
    )
    password_new_confirm = forms.CharField(
        label=_("New Password (again)"),
        widget=forms.PasswordInput(render_value=False),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordResetTokenForm, self).__init__(*args, **kwargs)

    def clean(self):
        clean_passwords(data=self.cleaned_data,
                        password1="password_new",
                        password2="password_new_confirm")

    def save(self, commit=True):
        """
        Saves the form and sets the user's password to be the value he/she
        typed in.
        """
        user = self.user
        if user:
            user.set_password(self.cleaned_data["password_new_confirm"])
            if commit:
                user.save()
            return user
