from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'^127.0.0.1:8000$', 'dataox.urls.host_index', name='host-index'),
    host(r'^127.0.0.2:8000$', 'dataox.urls.main', name='data'),
    host(r'^127.0.0.3:8000$', 'dataox.urls.backstage', name='backstage'),
    host(r'^127.0.0.4:8000$', 'dataox.urls.static', name='static'),
    host(r'^127.0.0.5:8000$', 'dataox.urls.course', name='course'),
    host(r'^127.0.0.6:8000$', 'dataox.urls.id', name='id-it'),
    host(r'^127.0.0.7:8000$', 'dataox.urls.equipment', name='equipment'),
    host(r'$x^', 'dataox.urls.empty', name='empty'),
)
