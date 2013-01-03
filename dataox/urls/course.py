from django.conf.urls.defaults import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from humfrey.desc import views as desc_views

from .main import handler404, handler500

urlpatterns = patterns('',
    url(r'^id/.*$', desc_views.IdView.as_view(), name='id'),
    url(r'^doc/$', desc_views.DocView.as_view(), name='doc-generic'),
    url(r'^doc.+$', desc_views.DocView.as_view(), name='doc'),
    url(r'^', include('dataox.course.urls', 'course')),
) + staticfiles_urlpatterns()
