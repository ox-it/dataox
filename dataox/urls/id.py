from django.conf.urls import patterns, url
from django_hosts import reverse_full

from humfrey.desc import views as desc_views
from humfrey.misc import views as misc_views

from .common import * #@UnusedWildImport

class IdView(desc_views.IdView):
    @property
    def doc_view(self):
        return reverse_full('data', 'doc-generic')
    @property
    def desc_view(self):
        return reverse_full('data', 'desc')

urlpatterns = patterns('',
    url(r'^.*', IdView.as_view(), {}, 'id'),
) + common_urlpatterns

handler404 = misc_views.SimpleView.as_view(template_name='404-id', context={'status_code':404})
