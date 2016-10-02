from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'authentication'


urlpatterns = [
    url(r"^authenticate/$",
        views.auth_login_register,
        name="auth_login_register"),
    url(r"^logout/$",
        views.auth_logout,
        name="auth_logout"),
    url(r"^password/reset/$",
        views.password_reset,
        name="password_reset"),
    url(r"^password/reset/confirm/"
        r"(?P<uidb64>[0-9A-Za-z_\-]+)/"
        r"(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.password_reset_confirm,
        name="password_reset_confirm"),
    url(r"^company/register/$",
        views.company_register,
        name="company_register"),
    url(r"^confirm_account/"
        r"(?P<uidb64>[0-9A-Za-z_\-]+)/"
        r"(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.account_confirm,
        name="account_confirm"),
]
