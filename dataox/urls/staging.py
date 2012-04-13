from django.conf.urls.defaults import url, include, patterns

urlpatterns = patterns(
    url('^main/', include('dataox.urls.main', 'host-data')),
    url('^admin/', include('dataox.urls.admin', 'host-admin')),
    url('^equipment/', include('dataox.urls.equipment', 'host-equipment')),
    url('^time-series/', include('dataox.urls.timeseries', 'host-timeseries')),
)
