from __future__ import unicode_literals

from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils.translation import ugettext_lazy as _

from .models import Applicant, Job


class ApplicantApplyForm(forms.ModelForm):
    resume = forms.FileField(
        widget=ClearableFileInput(
            attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        label=_('Name *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'name': 'name'}),
        max_length=120
    )
    email = forms.EmailField(
        label=_('Email *'),
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'name': 'email'}),
        max_length=120
    )
    university = forms.CharField(
        label=_('Education *'),
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'name': 'university'}),
        max_length=120
    )
    cover_letter = forms.CharField(
        label=_('Cover Letter'),
        widget=forms.Textarea(
            attrs={'style': 'height: 7em;',
                   'name': 'cover_letter',
                   'placeholder': 'Leave a message for the employer'}),
        max_length=1000,
        required=False
    )

    class Meta:
        model = Applicant
        fields = ('resume', 'name', 'email', 'university', 'cover_letter',)

    def __init__(self, *args, **kwargs):
        super(ApplicantApplyForm, self).__init__(*args, **kwargs)


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
    list_date_start = forms.DateTimeField(
        input_formats=['%m/%d/%Y %I:%M %p'],
        widget=forms.DateTimeInput(
            format='%m/%d/%Y %I:%M %p',
            attrs={'class': 'form-control',
                   'name': 'list_date_start',
                   'type': 'text'})
    )
    list_date_end = forms.DateTimeField(
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
                  'list_date_start', 'list_date_end',)

    def __init__(self, *args, **kwargs):
        super(JobCreateForm, self).__init__(*args, **kwargs)

    def clean_contact_email(self):
        """
        Return the lowercase value of the email.
        """
        return self.cleaned_data['contact_email'].lower()
