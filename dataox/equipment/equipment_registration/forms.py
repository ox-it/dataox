import uuid

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationFormTermsOfService, RegistrationFormUniqueEmail


class RegistrationForm(RegistrationFormTermsOfService,
                       RegistrationFormUniqueEmail):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    good_domains = frozenset(['alexdutton.co.uk'])

    def clean_email(self):
        email_domain = self.cleaned_data['email'].rsplit('@', 1)[1]
        if email_domain not in self.good_domains:
            raise forms.ValidationError(_("Registrations from your e-mail domain are not allowed."))
        return RegistrationFormUniqueEmail.clean_email(self)
    
    def clean(self):
        while True:
            username = uuid.uuid4().hex[:30]
            if not User.objects.filter(username=username).count():
                break
        self.cleaned_data['username'] = username
        return self.cleaned_data