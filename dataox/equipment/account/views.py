import uuid

import account.forms
import account.views
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.contrib.auth.models import User
from django_webauth.backends.webauth_ldap import LDAP_PROVISIONED_GROUP

from . import forms

class PatchSettings(View):
    patch_settings = {'DEFAULT_FROM_EMAIL': 'research.facilities@admin.ox.ac.uk'}
    def dispatch(self, request, *args, **kwargs):
        undefined = object()
        old_settings = {}
        for name in self.patch_settings:
            old_settings[name] = getattr(settings, name, undefined)
            setattr(settings, name, self.patch_settings[name])
        try:
            return super(PatchSettings, self).dispatch(request, *args, **kwargs)
        finally:
            for name, value in old_settings.iteritems():
                if value is undefined:
                    delattr(settings, name)
                else:
                    setattr(settings, name, value)

class WithUsablePassword(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_usable_password():
            raise PermissionDenied
        return super(WithUsablePassword, self).dispatch(request, *args, **kwargs)

class SignupView(PatchSettings, account.views.SignupView):
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

class LoginView(PatchSettings, account.views.LoginView):
    form_class = account.forms.LoginEmailForm
    template_name = 'equipment/account/login.html'

class ConfirmEmailView(PatchSettings, account.views.ConfirmEmailView):
    def get_template_names(self):
        return {
            "GET": ["equipment/account/email_confirm.html"],
            "POST": ["equipment/account/email_confirmed.html"],
        }[self.request.method]

class PasswordResetView(PatchSettings, account.views.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'equipment/account/password_reset.html'
    template_name_sent = 'equipment/account/password_reset_sent.html'

class PasswordResetTokenView(PatchSettings, account.views.PasswordResetTokenView):
    template_name = 'equipment/account/password_reset_token.html'
    template_name_fail = "equipment/account/password_reset_token_fail.html"

class ChangePasswordView(PatchSettings, WithUsablePassword, account.views.ChangePasswordView):
    template_name = "equipment/account/password_change.html"
