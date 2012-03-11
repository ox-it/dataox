from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views
from humfrey.images import views as images_views
from humfrey.misc import views as misc_views
from humfrey.graphviz import views as graphviz_views
from humfrey.elasticsearch import views as elasticsearch_views

from dataox.core.views import DatasetView, ExploreView, ExampleDetailView, ExampleResourceView, ExampleQueryView

urlpatterns = patterns('',
    (r'^$', misc_views.FeedView.as_view(rss_url='http://blogs.oucs.ox.ac.uk/opendata/feed/',
                                        template_name='index'), {}, 'index'),

    (r'^id/.*$', desc_views.IdView.as_view(), {}, 'id'),

    (r'^doc.+$', desc_views.DocView.as_view(), {}, 'doc'),
    (r'^doc/$', desc_views.DocView.as_view(), {}, 'doc-generic'),
    (r'^desc/$', desc_views.DescView.as_view(), {}, 'desc'),

    url(r'^search/$', elasticsearch_views.SearchView.as_view(), name='search'),

    (r'^datasets/$', DatasetView.as_view(), {}, 'datasets'),

    (r'^contact/$', misc_views.SimpleView.as_view(template_name='contact'), {}, 'contact'),
    (r'^help/$', misc_views.SimpleView.as_view(template_name='help'), {}, 'help'),
    (r'^legal-and-privacy/$', misc_views.SimpleView.as_view(template_name='legal'), {}, 'legal'),
    (r'^forbidden/$', misc_views.SimpleView.as_view(template_name='forbidden', context={'status_code': 403}), {}, 'forbidden'),

    (r'^explore/$', ExploreView.as_view(), {}, 'explore'),
    (r'^explore/resources/$', ExampleResourceView.as_view(), {}, 'explore-resource'),
    (r'^explore/queries/$', ExampleQueryView.as_view(), {}, 'explore-query'),

    (r'^explore/(?P<slug>[a-z\d-]+)/$', ExampleDetailView.as_view(), {}, 'example-detail'),
    (r'^explore/example:(?P<slug>[a-z\d-]+)/$', redirect_to, {'url': '/explore/%(slug)s/'}),

    (r'^pingback/', include('humfrey.pingback.urls.public', 'pingback')),
    (r'^sparql/', include('humfrey.sparql.urls', 'sparql')),
    (r'^browse/', include('humfrey.browse.urls', 'browse')),
    (r'^feeds/', include('dataox.feeds.urls', 'feeds')),

    (r'^external-image/$', images_views.ResizedImageView.as_view(), {}, 'resized-image'),

    (r'^graphviz/$', graphviz_views.GraphVizView.as_view(), {}, 'graphviz'),

    # as per http://www.w3.org/TR/void/#well-known
    (r'^.well-known/void$', redirect_to, {'url': '/datasets/', 'permanent': False}),
) + staticfiles_urlpatterns()

handler404 = misc_views.SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})

