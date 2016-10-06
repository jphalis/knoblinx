from django.contrib import admin

from .models import Activity

# Register your models here.


class ActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender_object', '__str__']
    list_display_links = ('id', 'sender_object',)
    readonly_fields = ['created', 'modified']

    class Meta:
        model = Activity


admin.site.register(Activity, ActivityAdmin)
