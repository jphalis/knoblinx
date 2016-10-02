from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Job

# Register your models here.


class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'contact_email',
                    'applicant_count', 'is_active',)
    list_display_links = ('id', 'title',)
    list_filter = ('company', 'created', 'modified', 'is_active',)
    raw_id_fields = ['company', 'applicants']
    fieldsets = (
        (None,
            {'fields': ('company', 'applicants', 'title', 'description',
                        'location', 'list_date_start', 'list_date_end',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('title', 'company__name', 'contact_email',)
    actions = ('enable', 'disable',)

    class Meta:
        model = Job

    def enable(self, request, queryset):
        """
        Updates is_active to be True.
        """
        queryset.update(is_active=True)
    enable.short_description = _("List selected jobs")

    def disable(self, request, queryset):
        """
        Updates is_active to be False.
        """
        queryset.update(is_active=False)
    disable.short_description = _("Remove selected jobs from listings")


admin.site.register(Job, JobAdmin)
