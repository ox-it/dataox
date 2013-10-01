import base64
import httplib
import logging
import random
import urllib2

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django_conneg.http import HttpError
from django_conneg.views import ContentNegotiatedView

from humfrey.update.models import Credential
from humfrey.utils.views import RedisView

logger = logging.getLogger(__name__)

class UserProfileImageView(RedisView, ContentNegotiatedView):
    url = 'https://mysite.nexus.ox.ac.uk/User%20Photos/Profile%20Pictures/ad-oak_{username}_{size}Thumb.jpg'
    sizes = {'small': 'S', 'medium': 'M', 'large': 'L'}
    
    def dispatch(self, request, *args, **kwargs):
        return super(UserProfileImageView, self).dispatch(request, *args, **kwargs)

    @method_decorator(login_required)
    def get(self, request, username, size):
        if not request.user.groups.filter(name='member').exists():
            raise PermissionDenied

        if size not in self.sizes:
            raise Http404
        
        url = self.url.format(username=username, size=self.sizes[size])
        key = 'dataox:sharepoint:user-profile-image:{username}:{size}'.format(username=username,
                                                                              size=size)
        
        redis = self.get_redis_client()
        value = redis.get(key)
        if value:
            content_type, content = value.split('\0', 1)
        else:
            content_type, content = self.get_image(url)
            redis.set(key, '\0'.join((content_type, content)))
            redis.expire(key, random.randrange(4*3600, 8*3600))
        
        response = HttpResponse(content)
        response['Content-type'] = content_type
        return response

    def get_image(self, url):
        """
        Retrieves the image from SharePoint.
        
        Returns a tuple of (content-type, content). content-type will likely
        always be 'image/jpeg', but we need to pass it through as-is.
        """
        try:
            credential = Credential.objects.get(user__username='opendata',
                                                url='https://sharepoint.nexus.ox.ac.uk/')
        except Credential.DoesNotExist:
            logger.warning("Missing SharePoint credentials", exc_info=1)
            raise HttpError(status_code=httplib.SERVICE_UNAVAILABLE)
            
        sp_request = urllib2.Request(url)
        sp_request.add_header('Authorization',
                              'Basic ' +
                              base64.b64encode(':'.join([credential.username,
                                                         credential.password])))
        
        try:
            response = urllib2.urlopen(sp_request)
            return response.headers['Content-type'], response.read()
        except urllib2.HTTPError as e:
            if e.code == 404:
                raise Http404
            if e.code in (401, 403):
                logger.warning("Failed authentication accessing profile image: %d",
                               e.code, exc_info=1)
                raise HttpError(status_code=httplib.SERVICE_UNAVAILABLE)
            raise
