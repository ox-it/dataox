from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to, direct_to_template

from humfrey.desc.views import IdView, DocView, DescView, SparqlView
from humfrey.images.views import ResizedImageView
from humfrey.misc.views import FeedView, SimpleView
from humfrey.graphviz.views import GraphVizView

from dataox.core.views import DatasetView, ExploreView, ExampleDetailView, ExampleResourceView, ExampleQueryView

urlpatterns = patterns('',
    (r'^$', FeedView(), {'rss_url': 'http://blogs.oucs.ox.ac.uk/opendata/feed/', 'template': 'index'}, 'index'),

    (r'^id/.*$', IdView(), {}, 'id'),

    (r'^doc.+$', DocView(), {}, 'doc'),
    (r'^doc/$', DocView(), {}, 'doc-generic'),
    (r'^desc/$', DescView(), {}, 'desc'),
    
    (r'^datasets/$', DatasetView(), {}, 'datasets'),
    (r'^sparql/$', SparqlView(), {}, 'sparql'),

    (r'^contact/$', direct_to_template, {'template': 'contact.html'}, 'contact'),
    (r'^help/$', direct_to_template, {'template': 'help.html'}, 'help'),

    (r'^forbidden/$', SimpleView(template_name='forbidden', context={'status_code': 403}), {}, 'forbidden'),

    (r'^explore/$', ExploreView(), {}, 'explore'),
    (r'^explore/resources/$', ExampleResourceView(), {}, 'explore-resource'),
    (r'^explore/queries/$', ExampleQueryView(), {}, 'explore-query'),

    (r'^explore/(?P<slug>[a-z\d-]+)/$', ExampleDetailView(), {}, 'example-detail'),
    (r'^explore/example:(?P<slug>[a-z\d-]+)/$', redirect_to, {'url': '/explore/%(slug)s/'}),

    (r'^pingback/', include('humfrey.pingback.urls')),
    (r'^update/', include('humfrey.update.urls')),

    (r'^external-image/$', ResizedImageView(), {}, 'resized-image'),

    (r'^graphviz/$', GraphVizView(), {}, 'graphviz'),
)

handler404 = SimpleView(template_name='404-main', context={'status_code':404})
handler500 = SimpleView(template_name='500', context={'status_code':500})

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

