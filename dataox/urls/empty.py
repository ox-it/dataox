from django.conf.urls.defaults import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .main import handler404, handler500

urlpatterns = patterns('',
) + staticfiles_urlpatterns()
