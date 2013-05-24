from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'data.ox.ac.uk', 'dataox.urls.main', name='data'),
    host(r'backstage.data.ox.ac.uk', 'dataox.urls.backstage', name='backstage'),
    host(r'static.data.ox.ac.uk', 'dataox.urls.static', name='static'),
    host(r'course.data.ox.ac.uk', 'dataox.urls.course', name='course'),
    host(r'www.research-facilities.ox.ac.uk', 'dataox.urls.equipment', name='equipment'),
    host(r'$x^', 'dataox.urls.empty', name='empty'),
    host(r'$x^', 'dataox.staging.urls', name='staging'),
)
