from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.utils.decorators import method_decorator


from oauth2app.authorize import Authorizer, MissingRedirectURI, AuthorizationException
from django_conneg.views import HTMLView

from . import forms

class AuthorizeView(HTMLView):
    template_name = 'oauth2/authorize'

    @method_decorator(login_required)
    def dispatch(self, request):
        self.authorizer = Authorizer()
        try:
            self.authorizer.validate(request)
        except MissingRedirectURI, e:
            return HttpResponseRedirect(reverse('oauth2:missing-redirect-url'))
        except AuthorizationException, e:
            # The request is malformed or invalid. Automatically
            # redirects to the provided redirect URL.
            return self.authorizer.error_redirect()
        return super(AuthorizeView, self).dispatch(request)
    
    def common(self, request):
        self.context.update({'authorizer': self.authorizer,
                             'client': self.authorizer.client,
                             'form': forms.AuthorizeForm(request.REQUEST or None)})

    def get(self, request):
        self.common(request)
        print self.authorizer.client.name
        return self.render()

    def post(self, request):
        self.common(request)
        if self.context['form'].is_valid():
            if 'accept' in request.POST:
                return self.authorizer.grant_redirect()
            else:
                return self.authorizer.error_redirect()
        return HttpResponseBadRequest()
            

class TokenView(HTMLView):
    pass

class MissingRedirectURLView(HTMLView):
    template_name = 'oauth2/missing-redirect-url'
    def get(self, request):
        return self.render()