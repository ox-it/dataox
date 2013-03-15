from django.conf.urls import patterns, include, url

from . import views

from account.views import LogoutView, DeleteView
from account.views import ConfirmEmailView
from account.views import ChangePasswordView, PasswordResetView, PasswordResetTokenView
from account.views import SettingsView
import django_webauth.views

urlpatterns = patterns('',
    url(r'^register/$', views.SignupView.as_view(), name='account_signup'),
    url(r'^login/$', views.LoginView.as_view(), name='account_login'),
    url(r"^confirm_email/(?P<key>\w+)/$", views.ConfirmEmailView.as_view(), name="account_confirm_email"),
    url(r"^password/$", views.ChangePasswordView.as_view(), name="account_password"),
    url(r"^password/reset/$", views.PasswordResetView.as_view(), name="account_password_reset"),
    url(r"^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$", PasswordResetTokenView.as_view(), name="account_password_reset_token"),

    url(r'^webauth/$', django_webauth.views.LoginView.as_view(), name='webauth_login'),
    url(r"^logout/$", django_webauth.views.LogoutView.as_view(), name="account_logout"),
#    url(r"^settings/$", SettingsView.as_view(), name="account_settings"),
#    url(r"^delete/$", DeleteView.as_view(), name="account_delete"),

)