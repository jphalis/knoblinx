from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Applicant, Job

# Register your models here.


class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'contact_email',
                    'applicant_count', 'is_active_job',)
    list_display_links = ('id', 'title',)
    list_filter = ('company', 'created', 'modified',)
    raw_id_fields = ['company', 'applicants']
    fieldsets = (
        (None,
            {'fields': ('company', 'applicants', 'title', 'description',
                        'location', 'list_date_start', 'list_date_end',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('title', 'company__name', 'contact_email',)

    class Meta:
        model = Job


class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'job_title',)
    list_display_links = ('id', 'user',)
    raw_id_fields = ['user']
    fieldsets = (
        (None,
            {'fields': ('user', 'resume', 'name', 'email', 'university',
                        'cover_letter',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('name', 'email',)

    class Meta:
        model = Applicant


admin.site.register(Job, JobAdmin)
admin.site.register(Applicant, ApplicantAdmin)
