import re
import urlparse

from django_hosts import middleware

class StagingMiddleware(object):
    hosts_middleware = middleware.HostsMiddleware()

    path_info_re = re.compile(r'/(?P<host>[a-z\-.]+)(?P<path>/.*)$')
    def process_request(self, request):
        path_info = self.path_info_re.match(request.path_info)
        if not path_info:
            return
        path_info = path_info.groupdict()
        request.original_http_host = request.META['HTTP_HOST']
        request.META['HTTP_HOST'] = path_info['host']
        request.path = request.path_info = path_info['path']

        if 'HTTP_REFERER' in request.META:
            referer = urlparse.urlparse(request.META['HTTP_REFERER'])
            path_info = self.path_info_re.match(referer.path)
            if referer.netloc != request.original_http_host or not path_info:
                return
            path_info = path_info.groupdict()

            request.META['HTTP_REFERER'] = urlparse.urlunparse((referer.scheme,
                                                                path_info['host'],
                                                                path_info['path'],
                                                                referer.params,
                                                                referer.query,
                                                                referer.fragment))

    def process_response(self, request, response):
        if hasattr(request, 'original_http_host'):
            request.path = request.path_info = '/%s%s' % (request.META['HTTP_HOST'], request.path_info)
            request.META['HTTP_HOST'] = request.original_http_host
        return response
