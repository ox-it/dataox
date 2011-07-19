from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
)

handler404 = lambda request: direct_to_tempate(request, template='404-main.html')
handler500 = lambda request: direct_to_tempate(request, template='500.html')
