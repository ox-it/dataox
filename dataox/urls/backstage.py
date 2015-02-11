from django.conf.urls import patterns, include, url
from django.contrib import admin
import django_webauth.views

from humfrey.misc import views as misc_views

from .common import * #@UnusedWildImport

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='backstage/index'), name='index'),
    url(r'^update/', include('humfrey.update.urls', 'update')),
    url(r'^stores/', include('humfrey.sparql.urls.admin', 'sparql-admin')),

    url(r'^accounts/webauth/$', django_webauth.views.LoginView.as_view(), name='account_webauth'),
    url(r'^accounts/logout/$', django_webauth.views.LogoutView.as_view(), name="account_logout"),

    url(r'^sharepoint/', include('dataox.sharepoint.urls', 'sharepoint')),

    url(r'^oauth2/', include('oauth2app.urls', 'oauth2app')),
    url(r'^admin/', admin.site.urls),
) + common_urlpatterns
