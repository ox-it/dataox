from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views
from humfrey.misc import views as misc_views
from humfrey.graphviz import views as graphviz_views
from humfrey.elasticsearch import views as elasticsearch_views

from dataox.core import views as core_views

search_args = {'opensearch_meta': {'ShortName': 'data.ox.ac.uk',
                                   'LongName': 'Open Data Service',
                                   'Description': 'Linked Open Data about the University of Oxford',
                                   'Contact': 'opendata@it.ox.ac.uk',
                                   'SyndicationRight': 'open'},
               'opensearch_images': [{'url': 'https://static.data.ox.ac.uk/favicon.ico'}]}

urlpatterns = [
    url(r'^$', misc_views.SimpleView.as_view(template_name='index'), name='index'),

    url(r'^id/.*$', desc_views.IdView.as_view(), name='id'),
    url(r'^doc.+$', desc_views.DocView.as_view(), name='doc'),
    url(r'^doc/$', desc_views.DocView.as_view(), name='doc-generic'),
    url(r'^desc/$', desc_views.DescView.as_view(), name='desc'),

    url(r'^search/$', elasticsearch_views.SearchView.as_view(**search_args), name='search'),

    url(r'^datasets/$', core_views.DatasetView.as_view(), name='datasets'),

    url(r'^contact/$', misc_views.SimpleView.as_view(template_name='contact'), name='contact'),
    url(r'^legal-and-privacy/$', misc_views.SimpleView.as_view(template_name='legal'), name='legal'),
    url(r'^forbidden/$', misc_views.SimpleView.as_view(template_name='forbidden', context={'status_code': 403}), name='forbidden'),
    url(r'^replacement-advice/$', misc_views.SimpleView.as_view(template_name='deprecation'), name='deprecation'),

    url(r'^explore/$', core_views.ExploreView.as_view(), name='explore'),
    url(r'^explore/resources/$', core_views.ExampleResourceView.as_view(), name='explore-resource'),
    url(r'^explore/queries/$', core_views.ExampleQueryView.as_view(), name='explore-query'),

    url(r'^explore/(?P<slug>[a-z\d-]+)/$', core_views.ExampleDetailView.as_view(), name='example-detail'),
    url(r'^explore/example:(?P<slug>[a-z\d-]+)/$', RedirectView.as_view(url='/explore/%(slug)s/')),

    url(r'^pingback/', include('humfrey.pingback.urls', 'pingback')),
    url(r'^sparql/', include('humfrey.sparql.urls.simple', 'sparql')),
    url(r'^feeds/', include('dataox.old_feeds.urls', 'old-feeds')),

    url(r'^graphviz/$', graphviz_views.GraphVizView.as_view(), name='graphviz'),

    # as per http://www.w3.org/TR/void/#well-known
    url(r'^.well-known/void$', RedirectView.as_view(url='/datasets/', permanent=False)),
    url(r'^.well-known/openorg$', core_views.OPDView.as_view(), name='openorg'),
] + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = core_views.ServerErrorView.as_view()

