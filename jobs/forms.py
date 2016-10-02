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
    cover_letter = forms.FileField(
        widget=ClearableFileInput(
            attrs={'class': 'form-control'})
    )

    class Meta:
        model = Applicant
        fields = ('resume', 'cover_letter',)

    def __init__(self, *args, **kwargs):
        super(ApplicantApplyForm, self).__init__(*args, **kwargs)


class JobCreateForm(forms.ModelForm):
    title = forms.CharField(
        label=_('Title'),
        widget=forms.TextInput(
            attrs={'placeholder': 'Position Title'}),
        max_length=120
    )
    location = forms.CharField(
        label=_('Location'),
        widget=forms.TextInput(
            attrs={'placeholder': 'Location of Job'}),
        max_length=80
    )
    description = forms.CharField(
        label=_('Job Description'),
        widget=forms.Textarea(
            attrs={'style': 'height: 7em;',
                   'placeholder': 'Say a little about the job'}),
        max_length=1000,
        required=False
    )
    # list_date_start = forms.DateTimeField(widget=DateTimeWidget(
    #     attrs={'class': 'form-control',
    #            'placeholder': 'Please click the calendar to the right'},
    #     usel10n=True, bootstrap_version=3, options=DateTimeOptions)
    # )
    # list_date_end = forms.DateTimeField(widget=DateTimeWidget(
    #     attrs={'class': 'form-control',
    #            'placeholder': 'Please click the calendar to the right'},
    #     usel10n=True, bootstrap_version=3, options=DateTimeOptions)
    # )
    contact_email = forms.EmailField(
        label=_('Contact Email'),
        widget=forms.EmailInput(),
        max_length=120
    )

    class Meta:
        model = Job
        fields = ('contact_email', 'title', 'description', 'location',)
                  #'list_date_start', 'list_date_end',

    def __init__(self, *args, **kwargs):
        super(JobCreateForm, self).__init__(*args, **kwargs)

    def clean_contact_email(self):
        """
        Return the lowercase value of the email.
        """
        return self.cleaned_data['contact_email'].lower()
