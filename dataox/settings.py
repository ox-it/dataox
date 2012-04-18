from __future__ import absolute_import

import imp
import os

from humfrey.settings.common import *

STAGING = True
DEBUG=False

ENDPOINT_URL = 'http://localhost:3030/public/query'
GRAPH_URL = 'http://localhost:3030/public/data'
SERVED_DOMAINS = ('data.ox.ac.uk',)

INSTALLED_APPS += (
    'dataox.core',
    'dataox.course',
    'dataox.resource',
    'dataox.feeds',
    'dataox.equipment',
    'humfrey.update',
    'humfrey.graphviz',
    'humfrey.browse',
    'humfrey.manage',
    'humfrey.elasticsearch',
    'openorg_timeseries',
    'django.contrib.admin',
    'object_permissions',
    'django_webauth',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dataox',
    }
}

ADMINS = (
    (config.get('admin:name'), config.get('admin:email')),
)

ROOT_URLCONF = 'dataox.urls.empty'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# django.contrib.staticfiles
STATIC_URL = '/static/'
STATIC_ROOT = relative_path(config['main:static_root'])
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'static'),
    os.path.join(imp.find_module('humfrey')[1], 'static'),
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    'django.core.context_processors.request',
    "django.contrib.messages.context_processors.messages",
    "dataox.core.context_processors.base_template_chooser"
)


ROOT_HOSTCONF = 'dataox.hosts'
DEFAULT_HOST = 'empty'

if STAGING:
    INSTALLED_APPS += ('dataox.staging',)
    MIDDLEWARE_CLASSES = ('dataox.staging.middleware.StagingMiddleware',) + MIDDLEWARE_CLASSES
    STATIC_URL = '/static.data.ox.ac.uk/'
    DEFAULT_HOST = 'staging'
    TEMPLATE_CONTEXT_PROCESSORS += ('dataox.staging.context_processors.staging',)

CACHE_BACKEND = 'memcached://127.0.0.1:3031/'

EMAIL_HOST = 'smtp.ox.ac.uk'
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get('email', 'user')
EMAIL_HOST_PASSWORD = config.get('email', 'password')
SERVER_EMAIL = 'dataox@opendata.nsms.ox.ac.uk'
DEFAULT_FROM_EMAIL = 'opendata@oucs.ox.ac.uk'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'object_permissions.backend.ObjectPermBackend',
    'django_webauth.backends.WebauthBackend',
)

MIDDLEWARE_CLASSES += (
    'django_conneg.support.middleware.BasicAuthMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
) + TEMPLATE_DIRS

THUMBNAIL_WIDTHS = (200, 400)
THUMBNAIL_HEIGHTS = (120, 80,)

ID_MAPPING = (
    ('http://data.ox.ac.uk/id/', 'http://data.ox.ac.uk/doc/', True),
    ('http://oxpoints.oucs.ox.ac.uk/id/', 'http://data.ox.ac.uk/doc:oxpoints/', False),
)

if STAGING:
    ID_MAPPING = tuple((a, b.split('/', 1)[1], c) for a,b,c in ID_MAPPING)


LONGLIVING_PUBSUB_WATCHERS += ('humfrey.elasticsearch.pubsub.update_search_indexes',)

TIME_SERIES_URI_BASE = "http://data.ox.ac.uk/id/time-series/"
TIME_SERIES_SERVER_ARGS = {'address': ('localhost', 4545),
                           'authkey': config.get('timeseries.authkey')}
TIME_SERIES_PATH = relative_path(config.get('timeseries:path'))

LONGLIVING_CLASSES |= set(['openorg_timeseries.longliving.database.DatabaseThread',
                           'humfrey.elasticsearch.longliving.indexer.Indexer'])

SOURCE_DIRECTORY = relative_path(config.get('update:source_directory'))
SOURCE_URL = config.get('update:source_url')

try:
    imp.find_module('openmeters')
except ImportError:
    pass
else:
    pass
    #LONGLIVING_CLASSES |= set(['openmeters.ion.DiscoveryThread',
    #                           'openmeters.ion.PollThread'])


UPDATE_TRANSFORMS += (
    'dataox.datasets.vacancies.RetrieveVacancies',
    'dataox.datasets.vacancies.checker.RetrieveVacanciesChecker',
)

UPDATE_FILES_DIRECTORY = os.path.join(MEDIA_ROOT, 'update-files')

ADDITIONAL_NAMESPACES.update({
    'vacancy': 'http://purl.org/openorg/vacancy/',
    'salary': 'http://purl.org/openorg/salary/',
    'meter': 'http://purl.org/meter/',
    'timeseries': 'http://purl.org/NET/time-series/',
    'oxnotation': 'http://data.ox.ac.uk/id/notation/',
    'xcri': 'http://xcri.org/profiles/1.2/',
    'mlo': 'http://purl.org/net/mlo/',

})

ELASTICSEARCH_SERVER = {'host': 'localhost',
                        'port': 9200}

UPDATE_FILES_DIRECTORY = os.path.join(MEDIA_ROOT, 'update-files')

if config.get('ckan:enabled') == 'true':
    CKAN_PATTERNS = {'name': 'ox-ac-uk-%s',
                     'title': '%s (University of Oxford)',
                     'author': '%s, University of Oxford',
                     'maintainer': '%s, University of Oxford'}
    CKAN_GROUPS |= set(['university-of-oxford'])
    CKAN_TAGS |= set(['oxford', 'university'])

ARCHIVE_PATH = relative_path(config.get('archive:path'))

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'
SESSION_COOKIE_SECURE = not DEBUG

VOCABULARY_URL_OVERRIDES = {
    'oxp': 'http://oxpoints.oucs.ox.ac.uk/ns.ttl',
}
