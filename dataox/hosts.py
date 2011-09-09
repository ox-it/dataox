from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'data.ox.ac.uk', 'dataox.urls.main', name='data'),
    host(r'time-series.data.ox.ac.uk', 'dataox.urls.timeseries', name='timeseries'),
    host(r'$x^', 'dataox.urls.empty', name='empty'),
)
