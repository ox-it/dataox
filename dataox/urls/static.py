from django.conf.urls import patterns, url

from humfrey.thumbnail import views as thumbnail_views

from .main import handler404, handler500

urlpatterns = patterns('',
    url(r'^thumbnail/$', thumbnail_views.ThumbnailView.as_view(), name='thumbnail'),
)
