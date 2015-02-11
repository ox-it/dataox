import imp
import os

from .components.static import *
from .components.email import *
from .components.humfrey import *
from .components.monkey_patches import *
from .components.celery import *

DEBUG = False
STAGING = False

# Localization
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'

INTERNAL_IPS = os.environ.get('DATAOX_INTERNAL_IPS', '127.0.0.1').split()

try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    with open(os.environ['SECRET_KEY_FILE']) as f:
        SECRET_KEY = f.read()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django_conneg',
    'django_hosts',
    'django_webauth',
    'guardian',
    'humfrey.desc',
    'humfrey.archive',
    'humfrey.ckan',
    'humfrey.elasticsearch',
    'humfrey.sparql',
    'humfrey.streaming',
    'humfrey.update',
    'humfrey.graphviz',
    'humfrey.manage',
    'humfrey.pingback',
    'humfrey.thumbnail',
    'humfrey.utils',
    'dataox.analytics',
    'dataox.core',
    'dataox.course',
    'dataox.equipment',
    'dataox.resource',
    'dataox.feeds',
    'oauth2app',
    'dataox.vacancy',
    'djcelery',
    'pipeline',
    'maintenancemode',
    'raven.contrib.django',
)

DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2',
                         'NAME': 'humfrey-dataox'}}

ADMINS = (
    (os.environ['DATAOX_ADMIN_NAME'], os.environ['DATAOX_ADMIN_EMAIL']),
)
MANAGERS = ADMINS

ROOT_URLCONF = 'dataox.urls.empty'
ROOT_HOSTCONF = 'dataox.hosts.production'
DEFAULT_HOST = 'empty'

OAUTH2_ACCESS_TOKEN_LENGTH = 20
OAUTH2_REFRESH_TOKEN_LENGTH = 20


TEMPLATE_DIRS = (
    os.path.join(imp.find_module('dataox')[1], 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "dataox.auth.context_processors.login_urls",
    "dataox.core.context_processors.base_template_chooser",
    "dataox.analytics.context_processors.do_not_track",
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django_webauth.backends.WebauthLDAP',
)

MIDDLEWARE_CLASSES = (
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'humfrey.base.middleware.AccessControlAllowOriginMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'oauth2app.middleware.OAuth2Middleware',
    'django_conneg.support.middleware.BasicAuthMiddleware',
    'humfrey.pingback.middleware.PingbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'dataox.auth.middleware.AuthenticatedAsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
)

# For django-registration
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
DEFAULT_HTTP_PROTOCOL = 'https'

SHELL_TRANSFORMS = {
    'spreadsheet2tei': ['/usr/bin/spreadsheet2tei', None],
}

REDIS_PARAMS = {'host': 'localhost',
                'port': 6379}

LOGIN_URL = '/accounts/webauth/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

SMTP_HOST = 'smtp.ox.ac.uk'

THUMBNAIL_WIDTHS = (200, 220, 400)
THUMBNAIL_HEIGHTS = (120, 80,)

SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ANONYMOUS_USER_ID = 0
GUARDIAN_RAISE_403 = True

from ..maintenancemode import MAINTENANCE_MODE

# Monkey patches
