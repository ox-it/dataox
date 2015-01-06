from django.utils.http import urlencode
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

def login_urls(request):
    path = request.get_full_path()
    login_url = settings.LOGIN_URL + '?' + urlencode({REDIRECT_FIELD_NAME: path})
    return {'login_url': login_url,
            'logout_url': settings.LOGOUT_URL}