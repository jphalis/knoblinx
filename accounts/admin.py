from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _

from authentication.forms import CompanyCreationForm, MyUserCreationForm
from .forms import CompanyChangeForm, MyUserChangeForm
from .models import Company, Degree, Experience, MyUser, School

# Register your models here.


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    list_display = ('id', '__str__', 'is_superuser', 'is_staff',
                    'is_confirmed',)
    list_display_links = ('id', '__str__',)
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_confirmed',
                   'account_type', 'university', 'gender',
                   'date_joined', 'modified',)
    prepopulated_fields = {'username': ["first_name", "last_name"], }
    raw_id_fields = ['university', 'degree']
    fieldsets = (
        (None,
            {'fields': ('email', 'password',)}),
        ('Basic information',
            {'fields': ('account_type', 'first_name', 'last_name', 'username',
                        'gender', 'profile_pic', 'video', 'resume',
                        'university', 'degree', 'gpa', 'hobbies',)}),
        ('Permissions',
            {'fields': ('is_active', 'is_confirmed', 'is_staff',
                        'is_superuser', 'user_permissions')}),
        (_('Dates'),
            {'fields': ('date_joined', 'last_login', 'modified',)}),
    )
    add_fieldsets = (
        (None,
            {'classes': ('wide',),
             'fields': ('email', 'first_name', 'last_name', 'username',
                        'password1', 'password2',)}),
    )
    readonly_fields = ('date_joined', 'last_login', 'modified',)
    search_fields = ('id', 'email', 'username', 'hobbies',)
    ordering = ('id',)
    filter_horizontal = ('user_permissions',)
    actions = ('enable', 'disable', 'confirm',)

    def enable(self, request, queryset):
        """
        Updates is_active to be True.
        """
        queryset.update(is_active=True)
    enable.short_description = _("Enable selected users")

    def disable(self, request, queryset):
        """
        Updates is_active to be False.
        """
        queryset.update(is_active=False)
    disable.short_description = _("Disable selected users")

    def confirm(self, request, queryset):
        """
        Confirms all selected users
        """
        queryset.update(is_confirmed=True)
    confirm.short_description = _("Confirm selected users")


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyChangeForm
    add_form = CompanyCreationForm

    list_display = ('id', 'name', 'username', 'is_active',)
    list_display_links = ('id', 'name',)
    list_filter = ('is_active', 'created', 'modified',)
    raw_id_fields = ['user', 'collaborators']
    prepopulated_fields = {'username': ["name"], }
    fieldsets = (
        (None,
            {'fields': ('user', 'collaborators', 'name', 'username',
                        'logo', 'website', 'bio')}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('user__get_full_name', 'user__email', 'name',
                     'collaborators__get_full_name', 'collaborators__email',)
    actions = ('enable', 'disable',)

    class Meta:
        model = Company

    def enable(self, request, queryset):
        """
        Updates is_active to be True.
        """
        queryset.update(is_active=True)
    enable.short_description = _("Enable selected drivers")

    def disable(self, request, queryset):
        """
        Updates is_active to be False.
        """
        queryset.update(is_active=False)
    disable.short_description = _("Disable selected drivers")


class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'company',)
    list_display_links = ('id', 'user',)
    list_filter = ('company',)
    raw_id_fields = ['user']
    fieldsets = (
        (None,
            {'fields': ('user', 'title', 'company', 'description',)}),
        (_('Dates'),
            {'fields': ('date_start', 'date_end',)}),
    )
    search_fields = ('user__get_full_name', 'user__email', 'title',
                     'company',)

    class Meta:
        model = Experience


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'email',)
    list_display_links = ('id', 'name',)
    fieldsets = (
        (None,
            {'fields': ('name', 'location', 'email',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
    )
    search_fields = ('name', 'location',)

    class Meta:
        model = School


class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)
    fieldsets = (
        (None,
            {'fields': ('name',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
    )
    search_fields = ('name',)

    class Meta:
        model = Degree


admin.site.unregister(Group)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Degree, DegreeAdmin)
