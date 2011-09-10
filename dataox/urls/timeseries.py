from django.conf.urls.defaults import *
from django.conf import settings

from humfrey.misc.views import SimpleView
urlpatterns = patterns('',
    (r'^', include('openorg_timeseries.urls', 'timeseries')),
    (r'^forbidden/$', SimpleView.as_view(template_name='forbidden', context={'status_code': 403}), {}, 'forbidden'),
)

handler404 = SimpleView.as_view(template_name='404-main', context={'status_code':404})
handler500 = SimpleView.as_view(template_name='500', context={'status_code':500})

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

