from django.conf.urls import patterns, url, include

from .common import * #@UnusedWildImport

urlpatterns = patterns('',
    url(r'^', include('dataox.course.urls')),
) + common_urlpatterns
