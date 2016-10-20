from django.contrib import admin
from django.utils.translation import ugettext as _

from django.contrib.contenttypes.models import ContentType

from accounts.models import MyUser
from .models import EmailConfirmation

# Register your models here.


class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'sent_date', 'key', 'key_valid',)
    list_display_links = ('__str__',)
    list_filter = ('sent_date',)
    raw_id_fields = ['user']
    fields = ('user', 'key', 'sent_date',)
    readonly_fields = ('sent_date',)
    search_fields = ('user__get_full_name', 'user__username',
                     'user__email',)
    actions = ('resend',)

    class Meta:
        model = EmailConfirmation

    def resend(self, request, queryset):
        """
        Re-sends a confirmation email to the selected users.
        """
        for obj in queryset:
            self.model.objects.send_confirmation(
                user=MyUser.objects.get(pk=obj.user.pk), request=request)
    resend.short_description = _("Re-send confirmation email")


admin.site.register(EmailConfirmation, EmailConfirmationAdmin)
