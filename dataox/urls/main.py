from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to, direct_to_template

from humfrey.desc.views import IdView, DocView, DescView
from humfrey.images.views import ResizedImageView
from humfrey.misc.views import FeedView, SimpleView
from humfrey.graphviz.views import GraphVizView
from humfrey.sparql.views import SparqlView

from dataox.core.views import DatasetView, ExploreView, ExampleDetailView, ExampleResourceView, ExampleQueryView

urlpatterns = patterns('',
    (r'^$', FeedView.as_view(), {'rss_url': 'http://blogs.oucs.ox.ac.uk/opendata/feed/', 'template': 'index'}, 'index'),

    (r'^id/.*$', IdView.as_view(), {}, 'id'),

    (r'^doc.+$', DocView.as_view(), {}, 'doc'),
    (r'^doc/$', DocView.as_view(), {}, 'doc-generic'),
    (r'^desc/$', DescView.as_view(), {}, 'desc'),
    
    (r'^datasets/$', DatasetView.as_view(), {}, 'datasets'),
    (r'^sparql/$', SparqlView.as_view(), {}, 'sparql'),

    (r'^contact/$', direct_to_template, {'template': 'contact.html'}, 'contact'),
    (r'^help/$', direct_to_template, {'template': 'help.html'}, 'help'),

    (r'^forbidden/$', SimpleView.as_view(template_name='forbidden', context={'status_code': 403}), {}, 'forbidden'),

    (r'^explore/$', ExploreView.as_view(), {}, 'explore'),
    (r'^explore/resources/$', ExampleResourceView.as_view(), {}, 'explore-resource'),
    (r'^explore/queries/$', ExampleQueryView.as_view(), {}, 'explore-query'),

    (r'^explore/(?P<slug>[a-z\d-]+)/$', ExampleDetailView.as_view(), {}, 'example-detail'),
    (r'^explore/example:(?P<slug>[a-z\d-]+)/$', redirect_to, {'url': '/explore/%(slug)s/'}),

    (r'^pingback/', include('humfrey.pingback.urls')),

    (r'^external-image/$', ResizedImageView.as_view(), {}, 'resized-image'),

    (r'^graphviz/$', GraphVizView.as_view(), {}, 'graphviz'),
)

handler404 = SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

