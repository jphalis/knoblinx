from __future__ import unicode_literals

from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext_lazy as _

from accounts.models import Degree, MyUser, School
from .models import Applicant, Job


class ApplicantApplyForm(forms.ModelForm):
    resume = forms.FileField(
        label=_('Resume *'),
        widget=ClearableFileInput(
            attrs={'class': 'form-control',
                   'name': 'resume'})
    )
    email = forms.EmailField(
        label=_('Email *'),
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'name': 'email'}),
        max_length=120
    )
    cover_letter = forms.CharField(
        label=_('Cover Letter'),
        widget=forms.Textarea(
            attrs={'style': 'height: 12em;',
                   'class': 'textarea editor-cls form-control',
                   'name': 'cover_letter',
                   'placeholder': 'Leave a message for the employer'}),
        max_length=5000,
        required=False
    )

    class Meta:
        model = Applicant
        fields = ('resume', 'email', 'cover_letter',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ApplicantApplyForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Return the lowercase value of the email.
        """
        return self.cleaned_data['email'].lower()


class JobCreateForm(forms.ModelForm):
    title = forms.CharField(
        label=_('Title *'),
        widget=forms.TextInput(
            attrs={'placeholder': 'Position title',
                   'class': 'form-control',
                   'name': 'title'}),
        max_length=120
    )
    location = forms.CharField(
        label=_('Location *'),
        widget=forms.TextInput(
            attrs={'placeholder': 'Location of job',
                   'class': 'form-control',
                   'name': 'location'}),
        max_length=120
    )
    contact_email = forms.EmailField(
        label=_('Contact Email *'),
        widget=forms.EmailInput(
            attrs={'placeholder': 'Contact email',
                   'class': 'form-control',
                   'name': 'title'}),
        max_length=120
    )
    min_gpa = forms.DecimalField(
        label=_('Minimum GPA *'),
        widget=forms.NumberInput(
            attrs={'placeholder': 'x.xx',
                   'class': 'form-control',
                   'name': 'min_gpa',
                   'min': 0,
                   'max': 4,
                   'step': 0.01}),
        initial=0.00,
        min_value=0,
        max_value=4,
        max_digits=3,
        decimal_places=2
    )
    universities = forms.ModelMultipleChoiceField(
        label=_('Universities *'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control',
                   'name': 'universities'}),
        queryset=[]
    )
    years = forms.MultipleChoiceField(
        label=_('Academic Years *'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control',
                   'name': 'years'}),
        choices=MyUser.YEAR_TYPES
    )
    degrees = forms.ModelMultipleChoiceField(
        label=_('Majors *'),
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'form-control',
                   'name': 'degrees'}),
        queryset=[]
    )
    list_date_start = forms.DateTimeField(
        label=_('Listing Start Date *'),
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            format='%m/%d/%Y %I:%M %p',
            attrs={'class': 'form-control',
                   'name': 'list_date_start',
                   'type': 'text'})
    )
    list_date_end = forms.DateTimeField(
        label=_('Listing End Date *'),
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            format='%m/%d/%Y %I:%M %p',
            attrs={'class': 'form-control',
                   'name': 'list_date_end',
                   'type': 'text'})
    )
    description = forms.CharField(
        label=_('Job Description *'),
        widget=forms.Textarea(
            attrs={'style': 'height: 18em;',
                   'class': 'textarea editor-cls form-control',
                   'name': 'description',
                   'placeholder': 'Say a little about the position'}),
        max_length=1000
    )

    class Meta:
        model = Job
        fields = ('contact_email', 'title', 'description', 'location',
                  'min_gpa', 'universities', 'years', 'degrees',
                  'list_date_start', 'list_date_end',)

    def __init__(self, *args, **kwargs):
        super(JobCreateForm, self).__init__(*args, **kwargs)
        self.fields['universities'].queryset = School.objects.active()
        self.fields['degrees'].queryset = Degree.objects.active()

    def clean_contact_email(self):
        """
        Return the lowercase value of the email.
        """
        return self.cleaned_data['contact_email'].lower()

    def clean_years(self):
        """
        Returns a list of the academic years allowed.
        """
        return ",".join(str(year) for year in self.cleaned_data['years'])
