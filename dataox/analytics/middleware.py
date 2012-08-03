from django.utils.cache import patch_vary_headers

class DoNotTrackMiddleware(object):
    """Adds a 'Vary: DNT' header to HTML responses."""

    def process_response(self, request, response):
        if getattr(request, 'using_analytics', False):
            patch_vary_headers(response, ['DNT'])
        return response