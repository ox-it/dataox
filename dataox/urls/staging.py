from django.conf.urls.defaults import url, include, patterns

from .main import handler404, handler500

urlpatterns = patterns(
    url('^main/', include('dataox.urls.main', 'host-data')),
    url('^backstage/', include('dataox.urls.backstage', 'host-backstage')),
    url('^equipment/', include('dataox.urls.equipment', 'host-equipment')),
)
