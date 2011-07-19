from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'data.ox.ac.uk', 'dataox.urls.main', name='data'),
    host(r'$x^', 'dataox.urls.empty', name='empty'),
)
