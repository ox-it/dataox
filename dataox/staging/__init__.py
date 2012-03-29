import inspect

from django.conf import settings

from django.http import HttpRequest
import django_hosts.reverse
import django.core.urlresolvers

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
