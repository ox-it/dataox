from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.misc import views as misc_views
import django_webauth.views

from .main import handler404, handler500

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='backstage/index'), name='index'),
    url(r'^feeds/', include('humfrey.feeds.urls', 'feeds')),
    url(r'^update/', include('humfrey.update.urls', 'update')),
    url(r'^stores/', include('humfrey.sparql.urls.admin', 'sparql-admin')),

    url(r'^accounts/login/$', django_webauth.views.LoginView.as_view(), name='account_webauth'),
    url(r'^accounts/logout/$', django_webauth.views.LogoutView.as_view(), name="account_logout"),

    url(r'^sharepoint/', include('dataox.sharepoint.urls', 'sharepoint')),

    url(r'^oauth2/', include('oauth2app.urls', 'oauth2app')),
    url(r'^admin/', admin.site.urls),
) + staticfiles_urlpatterns()
