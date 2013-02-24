from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views

from .main import handler404, handler500

# Not used, but could be hooked up to id.foo.ox.ac.uk

urlpatterns = patterns('',
    url(r'^.*', desc_views.IdView.as_view(), {}, 'id'),
) + staticfiles_urlpatterns()
