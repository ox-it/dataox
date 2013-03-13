from django.contrib.sites.models import Site, RequestSite

from registration import signals
from registration.backends.default import DefaultBackend


from .models import RegistrationProfile

class EquipmentBackend(DefaultBackend):
    def register(self, request, **kwargs):
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        first_name, last_name = kwargs['first_name'], kwargs['last_name']

        new_user = RegistrationProfile.objects.create_inactive_user(request,
                                                                    username, email, password,
                                                                    first_name, last_name)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user
    