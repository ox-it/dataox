from django.conf.urls.defaults import patterns, url, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .main import handler404, handler500

urlpatterns = patterns('',
    url(r'^', include('openorg_timeseries.urls.endpoint', 'timeseries-endpoint')),
) + staticfiles_urlpatterns()
