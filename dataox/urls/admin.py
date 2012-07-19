from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.misc import views as misc_views
from django_webauth.views import LogoutView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='manage/index'), name='index'),
    url(r'^time-series/', include('openorg_timeseries.urls.admin', 'timeseries')),
    url(r'^update/', include('humfrey.update.urls', 'update')),
    url(r'^time-series/', include('openorg_timeseries.urls.admin', 'timeseries-admin')),
    url(r'^stores/', include('humfrey.sparql.urls.admin', 'sparql-admin')),
    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^webauth/', include('django_webauth.urls', 'webauth')),
    url(r'^admin/', admin.site.urls),
) + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})
