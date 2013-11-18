from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views
from humfrey.misc import views as misc_views

from .main import handler500

urlpatterns = patterns('',
    url(r'^.*', desc_views.IdView.as_view(), {}, 'id'),
) + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404-id', context={'status_code':404})