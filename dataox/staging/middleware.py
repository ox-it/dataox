import re

from django_hosts import middleware

class StagingMiddleware(object):
    path_info_re = re.compile(r'/(?P<host>[a-z\-.]+)(?P<path>/.*)$')
    def process_request(self, request):
        path_info = self.path_info_re.match(request.path_info)
        if not path_info:
            return
        path_info = path_info.groupdict()
        request.META['HTTP_HOST'] = path_info['host']
        request.path_info = path_info['path']
