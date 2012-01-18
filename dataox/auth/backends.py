import inspect

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import User
from django.http import HttpRequest

class WebauthLDAPBackend(RemoteUserBackend):
    def authenticate(self, remote_user):
        username = self.clean_username(remote_user)
        user, created = User.objects.get_or_create(username=username)
        return self.configure_user(user)
        
    def configure_user(self, user):
        # Recurse up the call stack to find the request that was being
        # processed when this user logged in. If none is found,
        # request is set to None. Functional, but possibly hacky.
        # Don't do this at home, kids.
        for frame in inspect.getouterframes(inspect.currentframe()):
            request = frame[0].f_locals.get('request', None)
            if isinstance(request, HttpRequest):
                break

        if request:
            user.first_name = request.META.get('WEBAUTH_LDAP_GIVENNAME', user.first_name)
            user.last_name = request.META.get('WEBAUTH_LDAP_SN', user.last_name)
            user.email = request.META.get('WEBAUTH_LDAP_MAIL', user.email)

        return user