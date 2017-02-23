import re

from django_hosts import patterns, host

from dataox.settings import HOST_URLCONFS, HOST_DOMAINS

host_patterns = patterns('', *[
    host('^{}$'.format(re.escape(HOST_DOMAINS[name])),
         HOST_URLCONFS[name], name)
    for name in HOST_URLCONFS]
)
