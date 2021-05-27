from django.utils.deprecation import MiddlewareMixin
class AuthenticatedAsMiddleware(MiddlewareMixin):
    """
    Adds the authenticated user's username as a header on responses.
    """

    def process_response(self, request, response):
        if hasattr(request, 'user') and request.user.is_authenticated():
            response['X-Authenticated-As'] = request.user.username
        return response
