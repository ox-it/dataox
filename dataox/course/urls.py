from django.conf.urls.defaults import url, patterns

from humfrey.misc import views as misc_views
from humfrey.desc import views as desc_views

from . import views

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='course/index'), name='index'),
    url(r'^catalogues/$', views.CatalogView.as_view(), name='catalogues'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^doc.+$', desc_views.DocView.as_view(), name='doc'),
    url(r'^doc/$', desc_views.DocView.as_view(), name='doc-generic'),
)