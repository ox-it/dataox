from django.conf.urls.defaults import patterns, url

from humfrey.thumbnail import views as thumbnail_views
from humfrey.misc import views as misc_views

urlpatterns = patterns('',
    url(r'^thumbnail/$', thumbnail_views.ThumbnailView.as_view(), name='thumbnail'),
)

handler404 = misc_views.SimpleView.as_view(template_name='404', context={'status_code':404})
handler500 = misc_views.SimpleView.as_view(template_name='500', context={'status_code':500})