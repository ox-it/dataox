from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'id.conted.ox.ac.uk', 'dataox.urls.id', name='conted-id'),
    host(r'data.ox.ac.uk', 'dataox.urls.main', name='data'),
    host(r'admin.data.ox.ac.uk', 'dataox.urls.admin', name='admin'),
    host(r'time-series.data.ox.ac.uk', 'dataox.urls.timeseries', name='timeseries'),
    host(r'course.data.ox.ac.uk', 'dataox.urls.course', name='course'),
    host(r'www.research-facilities.ox.ac.uk', 'dataox.urls.equipment', name='equipment'),
    host(r'$x^', 'dataox.urls.empty', name='empty'),
    host(r'$x^', 'dataox.staging.urls', name='staging'),
)
