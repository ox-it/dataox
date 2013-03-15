import uuid

import account.forms
import account.views
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.contrib.auth.models import User
from django_webauth.backends.webauth_ldap import LDAP_PROVISIONED_GROUP

from . import forms

class NonLDAPProvisioned(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name=LDAP_PROVISIONED_GROUP).exists():
            raise PermissionDenied
        return super(NonLDAPProvisioned, self).dispatch(request, *args, **kwargs)

class SignupView(account.views.SignupView):
    form_class = forms.SignupForm
    template_name = 'equipment/account/signup.html'
    template_name_email_confirmation_sent = 'equipment/account/email_confirmation_sent.html'
    template_name_signup_closed = 'equipment/account/signup_closed.html'

    def generate_username(self, form):
        while True:
            username = uuid.uuid4().hex[:30]
            if not User.objects.filter(username=username).count():
                return username

    def create_user(self, form, commit=True, **kwargs):
        user = super(SignupView, self).create_user(form, False, **kwargs)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LoginView(account.views.LoginView):
    form_class = account.forms.LoginEmailForm
    template_name = 'equipment/account/login.html'

class ConfirmEmailView(account.views.ConfirmEmailView):
    def get_template_names(self):
        return {
            "GET": ["equipment/account/email_confirm.html"],
            "POST": ["equipment/account/email_confirmed.html"],
        }[self.request.method]

class PasswordResetView(NonLDAPProvisioned, account.views.PasswordResetView):
    template_name = 'equipment/account/password_reset.html'
    template_name_sent = 'equipment/account/password_reset_sent.html'

class ChangePasswordView(NonLDAPProvisioned, account.views.ChangePasswordView):
    template_name = "equipment/account/password_change.html"
