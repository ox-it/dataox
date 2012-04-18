import inspect

from django.conf import settings

from django.http import HttpRequest
import django_hosts.reverse
import django.core.urlresolvers

from humfrey.utils.resource import BaseResource
from humfrey.desc.views import IdView

"""
This Django app allows the use of django_hosts while remaining on the same
domain. It does the following:

 * monkey-patches reverse_full so that a URL of '//example.org/foo' becomes
   '/example.org/foo'
 * monkey-patches reverse to prepend the domain name, so that '/foo' becomes
   '/example.org/foo' (assuming that the HTTP Host header contains 'example.org'
 * provides middleware for setting the HTTP Host from the first component of
   path_info, so that the rest of the Django site (including reverse, as
   patched above) thinks that the HTTP_HOST meta parameter is e.g. 'example.org'

This means we don't have to mirror our production domain setup for staging.
"""

if settings.STAGING:
    original_reverse_full = django_hosts.reverse.reverse_full
    def new_reverse_full(*args, **kwargs):
        # Strip a leading '/', so we remain on the same host
        return original_reverse_full(*args, **kwargs)[1:]
    django_hosts.reverse.reverse_full = new_reverse_full

    original_reverse = django.core.urlresolvers.reverse
    def new_reverse(*args, **kwargs):
        for frame in inspect.getouterframes(inspect.currentframe()):
            request = frame[0].f_locals.get('request', None)
            if isinstance(request, HttpRequest):
                break
        else:
            raise Exception("Couldn't find request")

        return '/%s%s' % (request.META['HTTP_HOST'], original_reverse(*args, **kwargs))
    django.core.urlresolvers.reverse = new_reverse
    
    original_override_redirect = IdView.override_redirect
    def new_override_redirect(self, request, description_url, mimetypes):
        return original_override_redirect(self, request, '/' + description_url, mimetypes)
    IdView.override_redirect = new_override_redirect
    
    original_doc_url = BaseResource.doc_url.__get__
    def new_doc_url(self):
        return original_doc_url(self).split('/', 1)[1]
    BaseResource.doc_url = property(new_doc_url)
