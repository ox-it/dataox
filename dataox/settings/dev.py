from dataox.settings.base import *

DEBUG = True
STAGING = True

DOWNLOAD_CACHE = os.path.join(os.path.dirname(__file__),
                                      'download-cache')

IMAGE_CACHE_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                     'image-cache')

SOURCE_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                'source-data')

STATIC_ROOT = os.path.join(os.path.dirname(__file__),
                           'static-collected')

SESSION_COOKIE_SECURE = False

#_hosts_response_middleware_index = MIDDLEWARE_CLASSES.index('django_hosts.middleware.HostsResponseMiddleware')
#MIDDLEWARE_CLASSES = \
#    MIDDLEWARE_CLASSES[:_hosts_response_middleware_index] + \
#    ('debug_toolbar.middleware.DebugToolbarMiddleware',) + \
#    MIDDLEWARE_CLASSES[_hosts_response_middleware_index:]

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INSTALLED_APPS += ('debug_toolbar',)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

ROOT_HOSTCONF = 'dataox.hosts.dev'

ID_MAPPING = ()