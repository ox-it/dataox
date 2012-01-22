from django.conf.urls.defaults import patterns, url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.misc.views import SimpleView
urlpatterns = patterns('',
    url(r'^', include('openorg_timeseries.urls.endpoint', 'timeseries-endpoint')),
    url(r'^forbidden/$', SimpleView.as_view(template_name='forbidden', context={'status_code': 403}), name='forbidden'),
) + staticfiles_urlpatterns()

handler404 = SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})
