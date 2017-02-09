from django.conf.urls import url

from humfrey.thumbnail import views as thumbnail_views

from .main import handler404, handler500

urlpatterns = [
    url(r'^thumbnail/$', thumbnail_views.ThumbnailView.as_view(), name='thumbnail'),
]
