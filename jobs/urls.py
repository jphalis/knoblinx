from __future__ import unicode_literals

from django.conf.urls import url

from . import views
from .views import Delete


app_name = 'jobs'


urlpatterns = [
    url(r"^(?P<company_pk>\d+)/create/$",
        views.create, name="create"),
    url(r"^(?P<job_pk>\d+)/apply/$",
        views.apply, name="apply"),
    url(r'^(?P<job_pk>\d+)/delete/$',
        Delete.as_view(), name="delete"),
    url(r"^(?P<username>[\w.@+-]+)/(?P<job_pk>\d+)/$",
        views.detail, name="detail"),
    url(r"^(?P<username>[\w.@+-]+)/(?P<job_pk>\d+)/edit/$",
        views.edit, name="edit"),
]
