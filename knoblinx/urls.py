"""KnobLinx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from accounts import views as account_views
# from search import views as search_views
from search.views import SearchListView
from . import views


admin.site.site_header = "KnobLinx Administration"


urlpatterns = [


    url(r'^generate/', views.generate_data, name='generate_data'),




    # ADMIN
    url(r'^hidden/secure/knoblinx/admin/', include(admin.site.urls)),

    # GENERAL
    url(r'^$',
        views.home, name='home'),
    url(r'^ajax_top_banner_company/$',
        views.get_company_ajax, name='get_company_ajax'),
    url(r'^jobs/',
        include('jobs.urls', namespace='jobs')),
    url(r'^search/$',
        SearchListView.as_view(), name='search'),
    # url(r'^notifications/',
    #     include('notifications.urls',
    #     namespace='notifications')),
    url(r'^contact/',
        include('contact.urls', namespace='contact')),
    url(r'^terms/$',
        views.terms_of_use, name='terms_of_use'),
    url(r'^privacy/$',
        views.privacy_policy, name='privacy_policy'),

    # ACCOUNTS
    url(r'^(?P<username>[\w.@+-]+)/$',
        account_views.profile, name='profile'),
    url(r"^(?P<username>[\w-]+)/dashboard/$",
        account_views.company_dash,
        name="company_dash"),
    url(r'^accounts/',
        include('accounts.urls', namespace='accounts')),

    # AUTHENTICATION
    url(r'^auth/',
        include('authentication.urls', namespace='authentication')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += [] + static(settings.STATIC_URL,
                               document_root=settings.STATIC_ROOT)
    urlpatterns += [] + static(settings.MEDIA_URL,
                               document_root=settings.MEDIA_ROOT)
