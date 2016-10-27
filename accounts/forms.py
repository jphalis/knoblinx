"""
Glossary of accounts/forms.py:

- Add experience form
- Account settings form
- Account employer settings form
- Add collaborator form
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
from .models import Company, Degree, Experience, Hobby, MyUser, School

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
        label=_('First Name *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=50
    )
    last_name = forms.CharField(
        label=_('Last Name *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=50
    )
    email = forms.EmailField(
        label=_('Email *'),
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}),
        max_length=120
    )
    username = forms.SlugField(
        label=_('Username *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=120
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
    profile_pic = forms.ImageField(
        label=_('Profile Picture *'),
        widget=ClearableFileInput(
            attrs={'class': 'form-control'})
    )
    video = forms.CharField(
        label=_('Profile Video'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=250,
        required=False,
        help_text='Upload your video to <a href="https://www.youtube.com/upload">YouTube</a> first'
    )
    resume = forms.FileField(
        label=_('Resume *'),
        widget=ClearableFileInput(
            attrs={'class': 'form-control'})
    )
    opp_sought = forms.ChoiceField(
        label=_('Opportunity Sought *'),
        choices=(('', '---------'),) + MyUser.OPPORTUNITY_TYPES,
    )
    gender = forms.ChoiceField(
        label=_('Gender *'),
        choices=MyUser.GENDER_CHOICES
    )
    year = forms.ChoiceField(
        label=_('Academic Year *'),
        choices=(('', '---------'),) + MyUser.YEAR_TYPES,
    )
    gpa = forms.DecimalField(
        label=_('GPA *'),
        widget=forms.NumberInput(
            attrs={'min': 0,
                   'max': 4,
                   'step': 0.01,
                   'placeholder': 'x.xx'}),
        min_value=0,
        max_value=4,
        max_digits=3,
        decimal_places=2
    )
    undergrad_uni = forms.ModelChoiceField(
        label=_('Undergraduate University *'),
        queryset=[]
    )
    undergrad_degree = forms.ModelMultipleChoiceField(
        label=_('Undergraduate Degree(s) *'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control',
                   'name': 'undergrad_degree'}),
        queryset=[]
    )
    grad_uni = forms.ModelChoiceField(
        label=_('Graduate University'),
        queryset=[],
        required=False
    )
    grad_degree = forms.ModelMultipleChoiceField(
        label=_('Graduate Degree(s)'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control',
                   'name': 'grad_degree'}),
        queryset=[],
        required=False
    )
    degree_earned = forms.ChoiceField(
        label=_('Highest Degree Earned *'),
        choices=MyUser.DEGREE_TYPES
    )
    hobbies = forms.ModelMultipleChoiceField(
        label=_('Hobbies and Interests *'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control',
                   'name': 'hobbies'}),
        queryset=[],
    )
    # hobbies = forms.CharField(
    #     label=_("Hobbies and Interests"),
    #     widget=forms.TextInput(),
    #     max_length=250,
    #     required=False
    # )

    class Meta:
        model = MyUser
        fields = ('first_name', 'last_name', 'email', 'username', 'year',
                  'gpa', 'profile_pic', 'video', 'resume', 'opp_sought',
                  'gender', 'undergrad_uni', 'undergrad_degree', 'grad_uni',
                  'grad_degree', 'degree_earned', 'hobbies',
                  'password_new', 'password_new_confirm',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        _schools = School.objects.active()
        _degrees = Degree.objects.active()
        self.fields['undergrad_uni'].queryset = _schools
        self.fields['undergrad_degree'].queryset = _degrees
        self.fields['grad_uni'].queryset = _schools
        self.fields['grad_degree'].queryset = _degrees
        self.fields['hobbies'].queryset = Hobby.objects.active()

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        _email = self.cleaned_data['email'].lower()
        if self.initial.get('email') == _email:
            return _email
        if MyUser.objects.filter(
                Q(email__iexact=_email) & ~Q(pk=self.user.pk)).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return _email

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        _username = self.cleaned_data['username'].lower()
        if self.initial.get('username') == _username:
            return _username
        if MyUser.objects.filter(
                Q(username__iexact=_username) & ~Q(id=self.user.id)).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return _username

    def clean_video(self):
        """
        Convert the YouTube url into embed format if it's not already.
        """
        _url = self.cleaned_data['video']
        if 'embed/' not in _url and 'watch?v=' in _url:
            _url = _url.replace("watch?v=", "embed/")
        return _url

    def clean_opp_sought(self):
        _opp = self.cleaned_data['opp_sought']
        if not _opp:
            raise forms.ValidationError(
                _('You must choose your opportunity sought.'))
        return _opp

    def clean_year(self):
        _year = self.cleaned_data['year']
        if _year is None:
            raise forms.ValidationError(
                _('You must choose your current academic year.'))
        return _year

    def clean_degree_earned(self):
        _degree = self.cleaned_data['degree_earned']
        if not _degree:
            raise forms.ValidationError(
                _('You must select your degree(s) earned.'))
        return _degree

    def clean_undergrad_degree(self):
        _degrees = self.cleaned_data['undergrad_degree']
        if _degrees:
            if _degrees.count() > 2:
                raise forms.ValidationError(
                    _('You may only select up to 2 degrees.'))
            return _degrees
        raise forms.ValidationError(
            _('Please choose your undergraduate degree(s).'))

    def clean_grad_degree(self):
        _degrees = self.cleaned_data['grad_degree']
        if _degrees and _degrees.count() > 2:
            raise forms.ValidationError(
                _('You may only select up to 2 degrees.'))
        return _degrees

    def clean_hobbies(self):
        _hobbies = self.cleaned_data['hobbies']
        if not _hobbies:
            raise forms.ValidationError(
                _('You must select at least one hobby or interest.'))
        return _hobbies

    def clean_password_new_confirm(self):
        _password_confirm = self.cleaned_data['password_new_confirm']
        if not _password_confirm == '':
            clean_passwords(data=self.cleaned_data,
                            password1="password_new",
                            password2="password_new_confirm")
        return _password_confirm


class AccountEmployerSettingsForm(forms.ModelForm):
    """
    A form used for employers to update their account
    information.
    """
    first_name = forms.CharField(
        label=_('First Name *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=50
    )
    last_name = forms.CharField(
        label=_('Last Name *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=50
    )
    email = forms.EmailField(
        label=_('Email *'),
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}),
        max_length=120
    )
    username = forms.SlugField(
        label=_('Username *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        max_length=120
    )
    gender = forms.ChoiceField(
        choices=MyUser.GENDER_CHOICES
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
        fields = ('first_name', 'last_name', 'email', 'username', 'gender',
                  'password_new', 'password_new_confirm',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AccountEmployerSettingsForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Verify that the new email is not already taken.
        """
        _email = self.cleaned_data['email'].lower()
        if self.initial.get('email') == _email:
            return _email
        if MyUser.objects.filter(
                Q(email__iexact=_email) & ~Q(pk=self.user.pk)).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return _email

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        _username = self.cleaned_data['username'].lower()
        if self.initial.get('username') == _username:
            return _username
        if MyUser.objects.filter(
                Q(username__iexact=_username) & ~Q(id=self.user.id)).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return _username

    def clean_password_new_confirm(self):
        _password_confirm = self.cleaned_data['password_new_confirm']
        if not _password_confirm == '':
            clean_passwords(data=self.cleaned_data,
                            password1="password_new",
                            password2="password_new_confirm")
        return _password_confirm


class AddCollaboratorForm(forms.Form):
    email = email = forms.EmailField(
        label=_('Email *'),
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}),
        max_length=120,
        required=False
    )

    def clean_email(self):
        """
        Returns the email in a lowercase value.
        """
        return self.cleaned_data['email'].lower()


class CompanySettingsForm(forms.ModelForm):
    """
    A form used for companies to update their account
    information.
    """
    name = forms.CharField(
        label=_('Company Name *'),
        widget=forms.TextInput(),
        max_length=120
    )
    username = forms.SlugField(
        label=_('Company Username *'),
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
            attrs={'style': 'height: 7em;',
                   'placeholder': 'Tell us a little about your company'}),
        max_length=500,
        required=False
    )

    class Meta:
        model = Company
        fields = ('name', 'username', 'logo', 'website', 'bio',)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super(CompanySettingsForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        _username = self.cleaned_data['username'].lower()
        if self.initial.get('username') == _username:
            return _username
        if Company.objects.filter(
                Q(username__iexact=_username) &
                ~Q(pk=self.company.pk)).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return _username


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
        _email = self.cleaned_data['email']
        if self.initial.get('email') == _email:
            return _email
        if MyUser.objects.filter(email__iexact=_email).exists():
            raise forms.ValidationError(
                _('This email is already taken. Please try a different one.'))
        return _email

    def clean_username(self):
        """
        Verify that the new username is not already taken.
        """
        _username = self.cleaned_data['username'].lower()
        if self.initial.get('username') == _username:
            return _username
        if MyUser.objects.filter(username__iexact=_username).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return _username


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
        _username = self.cleaned_data['username'].lower()
        if self.initial.get('username') == _username:
            return _username
        if Company.objects.filter(username__iexact=_username).exists():
            raise forms.ValidationError(
                _('This username is already taken. '
                  'Please try a different one.'))
        return _username
