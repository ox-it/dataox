import uuid

from registration.forms import RegistrationFormTermsOfService, RegistrationFormUniqueEmail, RegistrationFormNoFreeEmail

class RegistrationForm(RegistrationFormTermsOfService,
                       RegistrationFormUniqueEmail,
                       RegistrationFormNoFreeEmail):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean_email(self):
        RegistrationFormUniqueEmail.clean_email(self)
        return RegistrationFormNoFreeEmail.clean_email(self)
    
    def clean(self):
        self.cleaned_data['username'] = uuid.uuid4().hex[:30]