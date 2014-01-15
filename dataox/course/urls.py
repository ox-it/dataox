from django.conf.urls import url, patterns

from humfrey.misc import views as misc_views

from . import views

urlpatterns = patterns('',
    url(r'^$', misc_views.SimpleView.as_view(template_name='course/index'), name='index'),
    url(r'^catalogues/$', views.CatalogView.as_view(), name='catalogues'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^id/.*$', views.IdView.as_view(), name='id'),
    url(r'^doc.+$', views.DocView.as_view(), name='doc'),
)
