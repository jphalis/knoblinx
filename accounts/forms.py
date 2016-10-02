"""
Glossary of accounts/forms.py:

- Add experience form
- Account settings form
- Company settings form
- MyUser change form (admin only)
- Company change form (admin only)
"""

from __future__ import unicode_literals

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Q
from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext_lazy as _

from core.utils import clean_passwords
from .models import Company, Experience, MyUser, School

# Create your forms here.


class ExperienceForm(forms.ModelForm):
    """
    A form used to create or modify resume experiences.
    """
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={'name': 'title',
                   'placeholder': 'Position title',
                   'class': 'form-control',
                   'type': 'text'}),
        max_length=120
    )
    company = forms.CharField(
        widget=forms.TextInput(
            attrs={'name': 'company',
                   'placeholder': 'Company name',
                   'class': 'form-control',
                   'type': 'text'}),
        max_length=120
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={'style': 'height: 12em;',
                   'name': 'description',
                   'class': 'textarea editor-cls form-control',
                   'placeholder': 'Say something about the position'}),
        max_length=500,
        required=False
    )
    date_start = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': 'text',
                   'name': 'date_start',
                   'class': 'form-control datemask',
                   'data-inputmask': '"alias": "mm/yyyy"'}),
        max_length=120,
        required=False
    )
    date_end = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': 'text',
                   'name': 'date_end',
                   'class': 'form-control datemask',
                   'data-inputmask': '"alias": "mm/yyyy"'}),
        max_length=120,
        required=False
    )

    class Meta:
        model = Experience
        fields = ('title', 'company', 'description', 'date_start', 'date_end',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ExperienceForm, self).__init__(*args, **kwargs)

    def clean_date_start(self):
        return datetime.strptime(
            self.cleaned_data['date_start'], '%m/%Y').strftime('%Y-%m-01')

    def clean_date_end(self):
        date_end = self.cleaned_data['date_end']
        if not date_end:
            return None
        return datetime.strptime(date_end, '%m/%Y').strftime('%Y-%m-01')


class AccountSettingsForm(forms.ModelForm):
    """
    A form used for users to update their account
    information.
    """
    first_name = forms.CharField(
        label=_('First Name*'),
        widget=forms.TextInput(),
        max_length=50
    )
    last_name = forms.CharField(
        label=_('Last Name*'),
        widget=forms.TextInput(),
        max_length=50
    )
    email = forms.EmailField(
        label=_('Email*'),
        widget=forms.EmailInput(),
        max_length=120
    )
    username = forms.SlugField(
        label=_('Username*'),
        widget=forms.TextInput(),
        max_length=120
    )
    profile_picture = forms.ImageField(
        label=_('Profile Picture'),
        widget=ClearableFileInput(),
        required=False
    )
    video = forms.CharField(
        label=_('Profile Video'),
        widget=forms.TextInput(),
        max_length=250,
        required=False,
        help_text='Upload your video to <a href="https://www.youtube.com/upload">YouTube</a> first'
    )
    resume = forms.FileField(
        widget=ClearableFileInput(),
        required=False
    )
    gender = forms.ChoiceField(
        choices=MyUser.GENDER_CHOICES
    )
    university = forms.TypedChoiceField(
        choices=[],
        empty_value='',
        required=False
    )
    degree = forms.CharField(
        widget=forms.TextInput(),
        max_length=120,
        required=False
    )
    gpa = forms.DecimalField(
        label=_('GPA*'),
        widget=forms.NumberInput(
            attrs={'min': 0,
                   'max': 4,
                   'step': 0.01}),
        min_value=0,
        max_value=4,
        max_digits=3,
        decimal_places=2
    )
    skills = forms.CharField(
        widget=forms.TextInput(),
        max_length=250,
        required=False
    )
    password_new = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(render_value=False),
        required=False
    )
    password_new_confirm = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(render_value=False),
        required=False
    )

    class Meta:
        model = MyUser
        fields = ('first_name', 'last_name', 'email', 'username', 'gpa',
                  'profile_picture', 'video', 'resume', 'gender', 'university',
                  'degree', 'skills', 'password_new', 'password_new_confirm',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        _schools = School.objects.active().values_list('name', flat=True)
        _choices = [('', '-- N/A --')] + [(x, x) for x in _schools]
        self.fields['university'].choices = _choices

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        value = self.cleaned_data['email'].lower()
        if self.initial.get('email') == value:
            return value
        if MyUser.objects.filter(
                Q(email__iexact=value) & ~Q(pk=self.user.pk)).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return value

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        value = self.cleaned_data['username'].lower()
        if self.initial.get('username') == value:
            return value
        if MyUser.objects.filter(
                Q(username__iexact=value) & ~Q(id=self.user.id)).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return value

    def clean_skills(self):
        return self.cleaned_data['skills']

    def clean_video(self):
        """
        Convert the YouTube url into embed format if it's not already.
        """
        url = self.cleaned_data['video']
        if 'embed/' not in url and 'watch?v=' in url:
            url = url.replace("watch?v=", "embed/")
        return url

    def clean_password_new_confirm(self):
        if not self.cleaned_data['password_new_confirm'] == '':
            clean_passwords(data=self.cleaned_data,
                            password1="password_new",
                            password2="password_new_confirm")
        return self.cleaned_data['password_new_confirm']


class CompanySettingsForm(forms.ModelForm):
    """
    A form used for companies to update their account
    information.
    """
    name = forms.CharField(
        label=_('Company Name'),
        widget=forms.TextInput(),
        max_length=120
    )
    username = forms.SlugField(
        label=_('Company Username'),
        widget=forms.TextInput(),
        max_length=120
    )
    logo = forms.ImageField(
        widget=ClearableFileInput(
            attrs={'class': 'form-control'}),
        help_text='Max height is 150px',
        required=False
    )
    website = forms.URLField(
        label=_('Website'),
        widget=forms.URLInput(),
        max_length=150,
        required=False
    )
    bio = forms.CharField(
        label=_('About'),
        widget=forms.Textarea(
            attrs={'style': 'height: 5em;',
                   'placeholder': 'Tell us a little about yourself'}),
        max_length=500,
        required=False
    )
    collaborators = forms.CharField(
        label=_('Collaborators'),
        help_text=_('These users will have administrative access '
                    'to your company.'),
        widget=forms.Textarea(),
        required=False
    )

    class Meta:
        model = Company
        fields = ('name', 'username', 'logo', 'website', 'bio',
                  'collaborators',)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super(CompanySettingsForm, self).__init__(*args, **kwargs)

    def clean_collaborators(self):
        """
        Add new collaborators based on the user's input.
        """
        value = self.cleaned_data['collaborators'].lower()
        for email in value:
            if not self.company.collaborators.filter(email__iexact=email):
                new_user = MyUser.objects.get(email=email)
                self.company.collaborators.add(new_user)
        return value

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        value = self.cleaned_data['username'].lower()
        if self.initial.get('username') == value:
            return value
        if Company.objects.filter(
                Q(username__iexact=value) & ~Q(id=self.company.id)).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return value


class MyUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    def __init__(self, *args, **kargs):
        super(MyUserChangeForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = MyUser
        fields = '__all__'

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        value = self.cleaned_data['email'].lower()
        if self.initial.get('email') == value:
            return value
        if MyUser.objects.filter(email__iexact=value).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return value

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        value = self.cleaned_data['username'].lower()
        if self.initial.get('username') == value:
            return value
        if MyUser.objects.filter(username__iexact=value).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return value


class CompanyChangeForm(forms.ModelForm):
    """
    A form for updating companies.
    """
    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, *args, **kargs):
        super(CompanyChangeForm, self).__init__(*args, **kargs)

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        value = self.cleaned_data['username'].lower()
        if self.initial.get('username') == value:
            return value
        if Company.objects.filter(username__iexact=value).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return value
