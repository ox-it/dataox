import httplib

from oauth2app.authenticate import Authenticator, AuthenticationException
from oauth2app.consts import REALM

class OAuth2Middleware(object):
    def process_request(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION', '')
        if not authorization.startswith('Bearer '):
            return

        authenticator = Authenticator()
        try:
            authenticator.validate(request)
        except AuthenticationException:
            return authenticator.error_response(content="You didn't authenticate.")

        request.user = authenticator.user

    def process_response(self, request, response):

        if response.status_code == httplib.UNAUTHORIZED:
            authenticate = response.get('WWW-Authenticate', None)
            if 'Bearer realm="' not in authenticate:
                if authenticate:
                    authenticate = 'Bearer realm="%s", %s' % (REALM, authenticate)
                else:
                    authenticate = 'Bearer realm="%s"' % REALM
            response['WWW-Authenticate'] = authenticate

        return response