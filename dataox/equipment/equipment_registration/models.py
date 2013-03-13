from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.db import transaction
from django.template import loader, RequestContext

import registration.models

class RegistrationManager(registration.models.RegistrationManager):
    @transaction.commit_on_success
    def create_inactive_user(self, request,
                             username, email, password,
                             first_name, last_name,
                             send_email=True):
        """
        Create a new, inactive ``User``, generate a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.
        
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.first_name, new_user.last_name = first_name, last_name
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(request)

        return new_user

class RegistrationProfile(registration.models.RegistrationProfile):
    class Meta:
        proxy = True

    objects = RegistrationManager()

    activation_email_template = 'equipment/registration/activation_email.eml'

    def send_activation_email(self, request):
        template = loader.get_template(self.activation_email_template)
        context = {'activation_key': self.activation_key,
                   'user': self.user}
        context = RequestContext(request, context)
        content = template.render_to_string(context)
        headers, body = content.split('\n\n', 1)

        headers = dict(tuple(h.split(': ', 1)) for h in headers.splitlines())
        recipient = headers['To'].split('<', 1)[1].rsplit('>', 1)[0]

        EmailMessage(body=body, headers=headers).send()
    
    
print "DDD", RegistrationProfile