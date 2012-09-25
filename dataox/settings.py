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
    'dataox.analytics',
    'dataox.vacancy',
    'humfrey.update',
    'humfrey.graphviz',
    'humfrey.manage',
    'humfrey.elasticsearch',
    'openorg_timeseries',
    'django.contrib.admin',
    'object_permissions',
    'django_webauth',
    'djcelery',
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
    "dataox.core.context_processors.base_template_chooser",
    "dataox.analytics.context_processors.do_not_track",
)


ROOT_HOSTCONF = 'dataox.hosts'
DEFAULT_HOST = 'empty'

if STAGING:
    INSTALLED_APPS = ('dataox.staging',) + INSTALLED_APPS
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
    'django.contrib.messages.middleware.MessageMiddleware',
    'dataox.analytics.middleware.DoNotTrackMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
) + TEMPLATE_DIRS

THUMBNAIL_WIDTHS = (200, 220, 400)
THUMBNAIL_HEIGHTS = (120, 80,)

ID_MAPPING = (
    ('http://data.ox.ac.uk/id/', 'http://data.ox.ac.uk/doc/', True),
    ('https://data.ox.ac.uk/id/equipment/', 'https://www.research-facilities.ox.ac.uk/view/', True),
    ('http://oxpoints.oucs.ox.ac.uk/id/', 'http://data.ox.ac.uk/doc:oxpoints/', False),
    ('http://id.conted.ox.ac.uk/', 'http://course.data.ox.ac.uk/doc:conted/', False),
)

HTML_MIMETYPES = ('application/xhtml+xml', 'text/html')

ID_MAPPING_REDIRECTS = (
    ('http://id.conted.ox.ac.uk/course/(?P<id>.*)', 'http://www.conted.ox.ac.uk/courses/details.php?id=%(id)s', HTML_MIMETYPES),
    ('http://id.conted.ox.ac.uk/presentation/(?P<id>.*)', 'http://www.conted.ox.ac.uk/%(id)s', HTML_MIMETYPES),
)

TIME_SERIES_URI_BASE = "http://data.ox.ac.uk/id/time-series/"
TIME_SERIES_SERVER_ARGS = {'address': ('localhost', 4545),
                           'authkey': config.get('timeseries.authkey')}
TIME_SERIES_PATH = relative_path(config.get('timeseries:path'))

SOURCE_DIRECTORY = relative_path(config.get('update:source_directory'))
SOURCE_URL = config.get('update:source_url')

try:
    imp.find_module('openmeters')
except ImportError:
    pass
else:
    pass


UPDATE_TRANSFORMS += (
    'dataox.vacancy.transform.RetrieveVacancies',
    'dataox.vacancy.transform.RetrieveVacanciesChecker',
    'dataox.oxpoints.transform.extents.OxpointsExtents',
)

UPDATE_FILES_DIRECTORY = os.path.join(MEDIA_ROOT, 'update-files')

ADDITIONAL_NAMESPACES.update({
    'adhoc': 'http://vocab.ox.ac.uk/ad-hoc-data-ox/',
    'cerif': 'http://spi-fm.uca.es/neologism/cerif#',
    'vacancy': 'http://purl.org/openorg/vacancy/',
    'salary': 'http://purl.org/openorg/salary/',
    'meter': 'http://purl.org/meter/',
    'timeseries': 'http://purl.org/NET/time-series/',
    'oxnotation': 'https://data.ox.ac.uk/id/notation/',
    'xcri': 'http://xcri.org/profiles/1.2/',
    'mlo': 'http://purl.org/net/mlo/',
    'spatialrelations': 'http://data.ordnancesurvey.co.uk/ontology/spatialrelations/',
    'prog': 'http://purl.org/prog/',

})

SHELL_TRANSFORMS = {
    'spreadsheet2tei': ['/usr/bin/spreadsheet2tei', None],
}

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
    'afn': None,
    'cc': 'http://creativecommons.org/schema.rdf',
    'fn': None,
    'oxnotation': None,
    'oxp': 'http://oxpoints.oucs.ox.ac.uk/ns.ttl',
    'pf': None,
}

# Celery

BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
CELERY_IMPORTS = (
    'humfrey.archive.tasks',
    'humfrey.ckan.tasks',
    'humfrey.elasticsearch.tasks',
    'humfrey.update.tasks',
)
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_LOG_COLOR = False

import djcelery
djcelery.setup_loader()

DEPENDENT_TASKS = {'humfrey.update.update': ('humfrey.ckan.upload_dataset_metadata',
                                             'humfrey.update.run_dependents',
                                             'humfrey.archive.update_dataset_archives',
                                             'humfrey.elasticsearch.update_indexes_after_dataset_update')}

ARCHIVE_STORES = ('public',)

ANONYMOUS_USER_ID = 0

RESOURCE_REGISTRY = 'dataox.resource.resource_registry'
DATASET_NOTATION = 'oxnotation:dataset'
GRAPH_BASE = 'https://data.ox.ac.uk/graph/'