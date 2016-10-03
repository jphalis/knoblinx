from __future__ import unicode_literals

from django.conf.urls import url

from . import views
from .views import ExpDelete


app_name = 'accounts'


urlpatterns = [
    url(r"^settings/$",
        views.account_settings, name="account_settings"),
    url(r"^settings/(?P<username>[\w-]+)/$",
        views.company_settings, name="company_settings"),
    url(r"^experience/(?P<exp_pk>\d+)/edit/$",
        views.exp_edit, name="exp_edit"),
    url(r'^experience/(?P<exp_pk>\d+)/delete/$',
        ExpDelete.as_view(), name="exp_delete"),
]
