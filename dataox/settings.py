import email.utils

import collections
import os
import platform

DEBUG = bool(os.environ.get('DJANGO_DEBUG'))
#DEBUG = True

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split() if not DEBUG else ['*']

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY and DEBUG:
    SECRET_KEY = 'Ui2ahcah9Lotheec1wahthoh4Ahnoo4aeGe1ooHengaishi5Bahshaeyahng4pai'

if 'DJANGO_ADMINS' in os.environ:
    ADMINS = [email.utils.parseaddr(addr.strip()) for addr in os.environ['DJANGO_ADMINS'].split(',')]
    MANAGERS = ADMINS

# Localization
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'

INTERNAL_IPS = os.environ.get('DJANGO_INTERNAL_IPS', '').split()

INSTALLED_APPS = (
    'django_celery_beat',
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
    'humfrey',
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
    'dataox',
    'dataox.core',
    'dataox.course',
    'dataox.equipment',
    'dataox.resource',
    'oauth2app',
    'dataox.old_feeds',
    'dataox.vacancy',
    'pipeline',
    'maintenancemode',
    'raven.contrib.django',
)

DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2',
                         'NAME': 'dataox'}}

ROOT_URLCONF = 'dataox.urls.empty'
ROOT_HOSTCONF = 'dataox.hosts'
DEFAULT_HOST = 'data'

STATIC_URL = os.environ['DJANGO_STATIC_URL']
STATICFILES_DIRS = ()
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT')

# OpenLayers should be installed as a system-wide package. To build the Debian
# package, clone git://github.com/ox-it/debian-packaging.git and build the
# package in the openlayers directory.
#distname, _, _ = platform.linux_distribution()
#if distname == 'Fedora':
#    STATICFILES_DIRS += (('lib/openlayers', '/usr/share/openlayers/www'),)
#elif distname == 'debian':
STATICFILES_DIRS += (('lib/openlayers', '/usr/share/javascript/openlayers'),
                     ('lib/jquery', '/usr/share/javascript/jquery'),
                     ('lib/jquery-cookie', '/usr/share/javascript/jquery-cookie'),
                     ('lib/jquery-ui', '/usr/share/javascript/jquery-ui'))
#else:
#    raise AssertionError("Unsupported distribution")
#del distname

PIPELINE = {
    'JAVASCRIPT': {
        'dataox': {'source_filenames': ('app/dataox-1.0.js',),
                   'output_filename': 'app/dataox-1.0.min.js'},
        'equipment': {'source_filenames': ('equipment/base.js',),
                      'output_filename': 'equipment.min.js'},
        'courses': {'source_filenames': ('app/courses-1.0.js',),
                    'output_filename': 'app/courses-1.0.min.js'},
        'html5shiv': {'source_filenames': ('lib/html5shiv.js',),
                      'output_filename': 'lib/html5shiv.min.js'},
        'oauth2': {'source_filenames': ('lib/oauth2/oauth2/oauth2.js',),
                   'output_filename': 'lib/oauth2.min.js'},
        'jquery.collapsible': {'source_filenames': ('lib/jquery-collapsible-content/js/jQuery.collapsible.js',),
                               'output_filename': 'lib/jquery.collapsible.min.js'},
    },
    'JS_COMPRESSOR': 'pipeline.compressors.closure.ClosureCompressor',
    'CLOSURE_BINARY': '/usr/bin/closure-compiler',
}

PIPELINE_CLOSURE_ARGUMENTS = '--jscomp_off uselessCode'
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'


OAUTH2_ACCESS_TOKEN_LENGTH = 20
OAUTH2_REFRESH_TOKEN_LENGTH = 20

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "dataox.auth.context_processors.login_urls",
                "dataox.core.context_processors.base_template_chooser",
            ],
        },
    },
]

IMAGE_TYPES = ('foaf:Image',)

SOURCE_URL = 'https://source.data.ox.ac.uk/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django_webauth.backends.WebauthLDAP',
    'djoxshib.backends.ShibbolethBackend',
)

MIDDLEWARE = (
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.PersistentRemoteUserMiddleware',
    'humfrey.base.middleware.AccessControlAllowOriginMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'oauth2app.middleware.OAuth2Middleware',
    'django_conneg.support.middleware.BasicAuthMiddleware',
    'humfrey.pingback.middleware.PingbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'dataox.auth.middleware.AuthenticatedAsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
)

DEFAULT_STORE = 'public'

# For django-registration
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
DEFAULT_HTTP_PROTOCOL = 'https'

ENDPOINT_QUERY = 'http://localhost:3030/public/query'
ENDPOINT_GRAPH = 'http://localhost:3030/public/data'

IMAGE_CACHE_DIRECTORY = os.environ.get('IMAGE_CACHE_DIRECTORY')
DOWNLOAD_CACHE = os.environ.get('DOWNLOAD_CACHE_DIRECTORY')
SOURCE_DIRECTORY = os.environ.get('SOURCE_DIRECTORY')

HUMFREY_FEEDS = {
    'organization': 'dataox.feeds.organization.OrganizationFeedView',
}

UPDATE_TRANSFORMS = (
    'dataox.vacancy.transform.RetrieveVacancies',
    'dataox.vacancy.transform.RetrieveVacanciesChecker',
    'dataox.oxpoints.transform.extents.OxpointsExtents',
    'humfrey.update.transform.base.Requires',
    'humfrey.update.transform.construct.Construct',
    'humfrey.update.transform.html.HTMLToXML',
    'humfrey.update.transform.normalize.Normalize',
    'humfrey.update.transform.retrieve.Retrieve',
    'humfrey.update.transform.sharepoint.SharePoint',
    'humfrey.update.transform.shell.Shell',
    'humfrey.update.transform.spreadsheet.GnumericToTEI',
    'humfrey.update.transform.spreadsheet.ODSToTEI',
    'humfrey.update.transform.spreadsheet.CSVToTEI',
    'humfrey.update.transform.union.Union',
    'humfrey.update.transform.upload.Upload',
    'humfrey.update.transform.vocabularies.VocabularyLoader',
    'humfrey.update.transform.xslt.XSLT',
)

SHELL_TRANSFORMS = {
    'spreadsheet2tei': ['/usr/bin/spreadsheet2tei', None],
}

EMAIL_HOST = 'smtp.ox.ac.uk'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[dataox] '
DEFAULT_FROM_EMAIL = 'opendata@it.ox.ac.uk'
# SERVER_EMAIL = 'Open Data Service Administrators <opendata-admin@maillist.ox.ac.uk>'

#SERVER_EMAIL = 'opendata-admin@maillist.ox.ac.uk'

REDIS_PARAMS = {'host': 'localhost',
                'port': 6379}

#LOGIN_URL = '/accounts/webauth/'
LOGIN_URL = '/shibboleth-login'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'


HOST_URLCONFS = collections.OrderedDict([
    ('data', 'dataox.urls.main'),
    ('backstage', 'dataox.urls.backstage'),
    ('static', 'dataox.urls.static'),
    ('course', 'dataox.urls.course'),
    ('id-it', 'dataox.urls.id'),
    ('equipment', 'dataox.urls.equipment'),
    ('empty', 'dataox.urls.empty'),
    ('docs', 'dataox.urls.empty'),
])

HOST_DOMAINS = {
    name: os.environ.get('DATAOX_DOMAIN_{}'.format(name.upper().replace('-', '_')),
                         '127.0.0.{}:8000'.format(i))
    for i, name in enumerate(HOST_URLCONFS, 1)
}


ID_MAPPING = (
    ('https://data.ox.ac.uk/id/equipment/',
     '//{equipment}/view:equipment/'.format(**HOST_DOMAINS), True),
    ('https://data.ox.ac.uk/id/facility/',
     '//{equipment}/view:facility/'.format(**HOST_DOMAINS), True),
    ('https://data.ox.ac.uk/id/',
     '//{data}/doc/'.format(**HOST_DOMAINS), True),
    ('http://oxpoints.oucs.ox.ac.uk/id/',
     '//{data}/doc:oxpoints/'.format(**HOST_DOMAINS), False),
    ('http://id.it.ox.ac.uk/',
     '//{data}/doc:it/'.format(**HOST_DOMAINS), True),
    ('http://id.conted.ox.ac.uk/',
     '//{course}/doc:conted/'.format(**HOST_DOMAINS), False),
)

HTML_MIMETYPES = ('application/xhtml+xml', 'text/html')

ID_MAPPING_REDIRECTS = (
    ('http://id.conted.ox.ac.uk/course/(?P<id>.*)', 'http://www.conted.ox.ac.uk/courses/details.php?id=%(id)s', HTML_MIMETYPES),
    ('http://id.conted.ox.ac.uk/presentation/(?P<id>.*)', 'http://www.conted.ox.ac.uk/%(id)s', HTML_MIMETYPES),
)

DOC_RDF_PROCESSORS = (
    'humfrey.desc.rdf_processors.doc_meta',
    'humfrey.desc.rdf_processors.formats',
)

IMAGE_PROPERTIES = ('foaf:depiction',)

ADDITIONAL_NAMESPACES = {
    'adhoc': 'http://vocab.ox.ac.uk/ad-hoc-data-ox/',
    'cerif': 'http://spi-fm.uca.es/neologism/cerif#',
    'exif': 'http://www.w3.org/2003/12/exif/ns#',
    'oosc': 'http://purl.org/openorg/space-configuration/',
    'prog': 'http://purl.org/prog/',
    'spatialrelations': 'http://data.ordnancesurvey.co.uk/ontology/spatialrelations/',
    'mlo' : 'http://purl.org/net/mlo/',
    'xcri': 'http://xcri.org/profiles/1.2/',
    'vacancy': 'http://purl.org/openorg/vacancy/',
    'meter': 'http://purl.org/meter/',
    'oxnotation': 'https://data.ox.ac.uk/id/notation/',
    'prog': 'http://purl.org/prog/',
    'oxcap': 'http://purl.ox.ac.uk/oxcap/ns/',
    'cat': 'http://purl.org/NET/catalog/',
}

ELASTICSEARCH_SERVER = {'host': 'localhost', 'port': 9200}

GRAPH_BASE = 'https://data.ox.ac.uk/graph/'

VOCABULARY_URL_OVERRIDES = {
    'afn': None,
    'cc': 'http://creativecommons.org/schema.rdf',
    'fn': None,
    'oxnotation': None,
    'oxp': 'http://oxpoints.oucs.ox.ac.uk/ns.ttl',
    'pf': None,
    'lyou': 'http://openorg.ecs.soton.ac.uk/linkingyou/linkingyou.ttl',
}

SMTP_HOST = 'smtp.ox.ac.uk'

THUMBNAIL_WIDTHS = (200, 220, 400)
THUMBNAIL_HEIGHTS = (120, 80,)

SESSION_COOKIE_SECURE = not DEBUG
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

MAINTENANCE_MODE_LOCK_DIRECTORY = os.environ.get('MAINTENANCE_MODE_LOCK_DIRECTORY')

# Celery

# CELERY_RESULT_BACKEND = "redis"
# CELERY_REDIS_HOST = "localhost"
# CELERY_REDIS_PORT = 6379
# CELERY_REDIS_DB = 0

DEPENDENT_TASKS = {'humfrey.update.update': ('humfrey.ckan.upload_dataset_metadata',
                                             'humfrey.update.run_dependents',
                                             'humfrey.archive.update_dataset_archives',
                                             'humfrey.elasticsearch.update_indexes_after_dataset_update')}

DATASET_NOTATION = 'oxnotation:dataset'

ANONYMOUS_USER_ID = 0
GUARDIAN_RAISE_403 = True

RESOURCE_REGISTRY = 'dataox.resource.resource_registry'

HUMFREY_FEEDS = {
    'organization': 'dataox.feeds.organization.OrganizationFeedView',
}

WEBAUTH_LDAP_USER = os.environ.get('WEBAUTH_LDAP_USER')

from .maintenancemode import MAINTENANCE_MODE
