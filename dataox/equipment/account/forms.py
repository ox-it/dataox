import account.forms
from django import forms
import account.models

from django.contrib.auth.models import User

class SignupForm(account.forms.SignupForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    good_domains = frozenset(['ouh.nhs.uk', 'ohis.nhs.uk', 'admin.ox.ac.uk', 'it.ox.ac.uk'])

    class Meta:
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields["username"]
        self.fields.keyOrder = ('first_name', 'last_name', 'email', 'password', 'password_confirm')

    def clean_email(self):
        email = super(SignupForm, self).clean_email()
        domain = email.rsplit('@', 1)[-1]
        if domain not in self.good_domains:
            raise forms.ValidationError('Registrations from your email domain are not permitted.')
        return self.cleaned_data['email']

class PasswordResetForm(account.forms.PasswordResetForm):
    def clean_email(self):
        email = super(PasswordResetForm, self).clean_email()
        try:
            user = User.objects.get(email=email)
            if user.has_unusable_password():
                raise forms.ValidationError('Your password cannot be reset.')
        except User.DoesNotExist:
            raise forms.ValidationError('Your password cannot be reset.')
        return email
