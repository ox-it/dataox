import imp
import os
import platform

DEBUG = False
STAGING = False

# Localization
TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'

INTERNAL_IPS = (
    '127.0.0.1',       # localhost
    '129.67.101.12',   # oucs-alexd.oucs.ox.ac.uk
    '192.168.122.1',   # virt-manager host
)

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
    'humfrey.feeds',
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
    'dataox.old_feeds',
    'dataox.vacancy',
    'djcelery',
    'pipeline',
    'maintenancemode',
    'raven.contrib.django',
)

DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2',
                         'NAME': 'humfrey-dataox'}}

ADMINS = (
    ('data.ox.ac.uk administrators', 'opendata-admin@maillist.ox.ac.uk'),
)
MANAGERS = ADMINS

ROOT_URLCONF = 'dataox.urls.empty'
ROOT_HOSTCONF = 'dataox.hosts'
DEFAULT_HOST = 'empty'

STATIC_URL = '//static.data.ox.ac.uk/'
STATICFILES_DIRS = (
    os.path.join(imp.find_module('dataox')[1], 'static'),
    os.path.join(imp.find_module('humfrey')[1], 'static'),
)

# OpenLayers should be installed as a system-wide package. To build the Debian
# package, clone git://github.com/ox-it/debian-packaging.git and build the
# package in the openlayers directory.
distname, _, _ = platform.linux_distribution()
if distname == 'Fedora':
    STATICFILES_DIRS += (('lib/openlayers', '/usr/share/openlayers/www'),)
elif distname == 'debian':
    STATICFILES_DIRS += (('lib/openlayers', '/usr/share/javascript/openlayers'),
                         ('lib/jquery', '/usr/share/javascript/jquery'),
                         ('lib/jquery-cookie', '/usr/share/javascript/jquery-cookie'),
                         ('lib/jquery-ui', '/usr/share/javascript/jquery-ui'),
                         ('lib/datatables', '/usr/share/javascript/datatables'))
else:
    raise AssertionError("Unsupported distribution")
del distname

PIPELINE_JS = {
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
}

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.closure.ClosureCompressor'
PIPELINE_CLOSURE_ARGUMENTS = '--jscomp_off uselessCode'
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'


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

IMAGE_TYPES = ('foaf:Image',)

SOURCE_URL = 'https://source.data.ox.ac.uk/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django_webauth.backends.WebauthLDAP',
)

MIDDLEWARE_CLASSES = (
    'django_hosts.middleware.HostsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'humfrey.base.middleware.AccessControlAllowOriginMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
   # 'oauth2app.middleware.OAuth2Middleware',
    'django_conneg.support.middleware.BasicAuthMiddleware',
    'humfrey.pingback.middleware.PingbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'dataox.auth.middleware.AuthenticatedAsMiddleware',
)

DEFAULT_STORE = 'public'

# For django-registration
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
DEFAULT_HTTP_PROTOCOL = 'https'

ENDPOINT_QUERY = 'http://localhost:3030/public/query'
ENDPOINT_GRAPH = 'http://localhost:3030/public/data'

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
SERVER_EMAIL = 'Open Data Service Administrators <opendata-admin@maillist.ox.ac.uk>'

SERVER_EMAIL = 'opendata-admin@maillist.ox.ac.uk'

REDIS_PARAMS = {'host': 'localhost',
                'port': 6379}

LOGIN_URL = '/accounts/webauth/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

ID_MAPPING = (
    ('https://data.ox.ac.uk/id/equipment/', 'https://www.research-facilities.ox.ac.uk/view:equipment/', True),
    ('https://data.ox.ac.uk/id/facility/', 'https://www.research-facilities.ox.ac.uk/view:facility/', True),
    ('https://data.ox.ac.uk/id/', 'https://data.ox.ac.uk/doc/', True),
    ('http://oxpoints.oucs.ox.ac.uk/id/', 'https://data.ox.ac.uk/doc:oxpoints/', False),
    ('http://id.it.ox.ac.uk/', 'https://data.ox.ac.uk/doc:it/', True),
    ('http://id.conted.ox.ac.uk/', 'https://course.data.ox.ac.uk/doc:conted/', False),
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

SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

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
CELERYD_LOG_LEVEL = 'DEBUG'

import djcelery
djcelery.setup_loader()

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

from .maintenancemode import MAINTENANCE_MODE

# Monkey patches

import sys
import rdflib
import urllib2

if map(int, rdflib.__version__.split('.')[0]) < 3:
    from datetime import date, time, datetime
    l = sys.modules['rdflib.Literal']
    _XSD_NS = l._XSD_NS
    l._PythonToXSD = [
        (basestring, (None,None)),
        (float     , (None,_XSD_NS[u'float'])),
        (bool      , (lambda i:str(i).lower(),_XSD_NS[u'boolean'])),
        (int       , (None,_XSD_NS[u'integer'])),
        (long      , (None,_XSD_NS[u'long'])),
        (datetime  , (lambda i:i.isoformat(),_XSD_NS[u'dateTime'])),
        (date      , (lambda i:i.isoformat(),_XSD_NS[u'date'])),
        (time      , (lambda i:i.isoformat(),_XSD_NS[u'time'])),
    ]
    del date, datetime, time, l, _XSD_NS

# http://bugs.python.org/issue9639 (Python 2.6.6 regression)


if sys.version_info[:2] == (2, 6) and sys.version_info[2] >= 6:
    def fixed_http_error_401(self, req, fp, code, msg, headers):
        url = req.get_full_url()
        response = self.http_error_auth_reqed('www-authenticate',
                                          url, req, headers)
        self.retried = 0
        return response

    urllib2.HTTPBasicAuthHandler.http_error_401 = fixed_http_error_401
del rdflib, sys, urllib2
