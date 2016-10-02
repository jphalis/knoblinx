from django.conf.urls import url

from . import views


app_name = 'tags'


urlpatterns = [
    url(r'^(?P<tag>[\w-]+)/$', views.tagged_list, name='tagged_list')
]
