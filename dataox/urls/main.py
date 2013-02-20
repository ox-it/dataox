from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views
from humfrey.misc import views as misc_views
from humfrey.graphviz import views as graphviz_views
from humfrey.elasticsearch import views as elasticsearch_views

from dataox.core import views as core_views

search_args = {'opensearch_meta': {'ShortName': 'data.ox.ac.uk',
                                   'LongName': 'Open Data Service',
                                   'Description': 'Linked Open Data about the University of Oxford',
                                   'Contact': 'opendata@oucs.ox.ac.uk',
                                   'SyndicationRight': 'open'},
               'opensearch_images': [{'url': 'https://static.data.ox.ac.uk/favicon.ico'}]}

urlpatterns = patterns('',
    (r'^$', misc_views.SimpleView.as_view(template_name='index'), {}, 'index'),

    (r'^id/.*$', desc_views.IdView.as_view(), {}, 'id'),

    (r'^doc.+$', desc_views.DocView.as_view(), {}, 'doc'),
    (r'^doc/$', desc_views.DocView.as_view(), {}, 'doc-generic'),
    (r'^desc/$', desc_views.DescView.as_view(), {}, 'desc'),

    url(r'^search/$', elasticsearch_views.SearchView.as_view(**search_args), name='search'),

    (r'^datasets/$', core_views.DatasetView.as_view(), {}, 'datasets'),

    (r'^contact/$', misc_views.SimpleView.as_view(template_name='contact'), {}, 'contact'),
    (r'^legal-and-privacy/$', misc_views.SimpleView.as_view(template_name='legal'), {}, 'legal'),
    (r'^forbidden/$', misc_views.SimpleView.as_view(template_name='forbidden', context={'status_code': 403}), {}, 'forbidden'),

    (r'^explore/$', core_views.ExploreView.as_view(), {}, 'explore'),
    (r'^explore/resources/$', core_views.ExampleResourceView.as_view(), {}, 'explore-resource'),
    (r'^explore/queries/$', core_views.ExampleQueryView.as_view(), {}, 'explore-query'),

    (r'^explore/(?P<slug>[a-z\d-]+)/$', core_views.ExampleDetailView.as_view(), {}, 'example-detail'),
    (r'^explore/example:(?P<slug>[a-z\d-]+)/$', redirect_to, {'url': '/explore/%(slug)s/'}),

    (r'^pingback/', include('humfrey.pingback.urls', 'pingback')),
    (r'^sparql/', include('humfrey.sparql.urls.simple', 'sparql')),
    (r'^feeds/', include('dataox.old_feeds.urls', 'old-feeds')),

    (r'^graphviz/$', graphviz_views.GraphVizView.as_view(), {}, 'graphviz'),

    # as per http://www.w3.org/TR/void/#well-known
    (r'^.well-known/void$', redirect_to, {'url': '/datasets/', 'permanent': False}),
) + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = core_views.ServerErrorView.as_view()

