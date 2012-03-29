from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'data.ox.ac.uk', 'dataox.urls.main', name='data'),
    host(r'admin.data.ox.ac.uk', 'dataox.urls.admin', name='admin'),
    host(r'time-series.data.ox.ac.uk', 'dataox.urls.timeseries', name='timeseries'),
    host(r'equipment.data.ox.ac.uk', 'dataox.urls.equipment', name='equipment'),
    host(r'$x^', 'dataox.urls.empty', name='empty'),
)
