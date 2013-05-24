from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
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

    url(r'^account/login/$', auth_views.login, name='account_login'),
    url(r'^account/webauth/$', django_webauth.views.LoginView.as_view(), name='account_webauth'),
    url(r"^account/logout/$", django_webauth.views.LogoutView.as_view(), name="account_logout"),

    url(r'^oauth2/', include('dataox.oauth2.urls', 'oauth2')),
    url(r'^admin/', admin.site.urls),
) + staticfiles_urlpatterns()
