from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.misc import views as misc_views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='manage/index'), name='index'),
    url(r'^pingback/', include('humfrey.pingback.urls.admin', 'pingback')),
    url(r'^update/', include('humfrey.update.urls', 'update')),
    url(r'^time-series/', include('openorg_timeseries.urls.admin', 'timeseries-admin')),
    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', auth_views.logout, name='logout'),
    url(r'^webauth/login/$', redirect_to, name='webauth-login'),
    url(r'^webauth/logout/$', redirect_to, name='webauth-logout'),
    url(r'^admin/', admin.site.urls),
) + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404-empty', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})
