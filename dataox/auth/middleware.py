class AuthenticatedAsMiddleware(object):
    """
    Adds the authenticated user's username as a header on responses.
    """

    def process_response(self, request, response):
        if request.user.is_authenticated():
            response['X-Authenticated-As'] = request.user.username
        return response