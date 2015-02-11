from django.conf.urls import url, include, patterns

from humfrey.misc import views as misc_views

from .common import * #@UnusedWildImport

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='host-index'), name='index'),
) + common_urlpatterns
