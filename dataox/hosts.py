import collections
import os
import re

from django_hosts import patterns, host

hosts = collections.OrderedDict([
    ('data', 'dataox.urls.main'),
    ('backstage', 'dataox.urls.backstage'),
    ('static', 'dataox.urls.static'),
    ('course', 'dataox.urls.course'),
    ('id-it', 'dataox.urls.id'),
    ('equipment', 'dataox.urls.equipment'),
    ('empty', 'dataox.urls.empty'),
])

host_patterns = patterns('', *[
    host('^{}$'.format(re.escape(os.environ.get('DATAOX_DOMAIN_{}'.format(name.upper()),
                                                '127.0.0.{}:8000'.format(i)))),
         hosts[name], name)
    for i, name in enumerate(hosts, 1)]
)
