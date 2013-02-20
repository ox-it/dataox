import imp
import os

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
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django_conneg',
    'django_longliving',
    'django_hosts',
    'django_webauth',
    'object_permissions',
    'humfrey.desc',
    'humfrey.archive',
    'humfrey.ckan',
    'humfrey.elasticsearch',
    'humfrey.sparql',
    'humfrey.update',
    'humfrey.graphviz',
    'humfrey.manage',
    'humfrey.pingback',
    'humfrey.thumbnail',
    'humfrey.utils',
    'openorg_timeseries',
    'dataox.analytics',
    'dataox.core',
    'dataox.course',
    'dataox.equipment',
    'dataox.resource',
    'dataox.feeds',
    'dataox.vacancy',
    'djcelery',
    'pipeline',
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

PIPELINE = True
PIPELINE_JS = {
    'dataox': {'source_filenames': ('app/dataox-1.0.js',),
               'output_filename': ('app/dataox-1.0.min.js')},
    'equipment': {'source_filenames': ('equipment/base.js',),
                  'output_filename': ('equipment.min.js')},
    'courses': {'source_filenames': ('app/courses-1.0.js',),
                'output_filename': ('lib/courses-1.0.min.js')},
    'html5shiv': {'source_filenames': ('lib/html5shiv.js',),
                  'output_filename': ('lib/html5shiv.min.js')},
    'oauth2': {'source_filenames': ('lib/oauth2/oauth2/oauth2.js',),
               'output_filename': ('lib/oauth2.min.js')},
    'jquery': {'source_filenames': ('lib/jquery/src/intro.js',
                                    'lib/jquery/src/core.js',
                                    'lib/jquery/src/intro.js',
                                    'lib/jquery/src/callbacks.js',
                                    'lib/jquery/src/deferred.js',
                                    'lib/jquery/src/support.js',
                                    'lib/jquery/src/data.js',
                                    'lib/jquery/src/queue.js',
                                    'lib/jquery/src/attributes.js',
                                    'lib/jquery/src/event.js',
                                    'lib/jquery/src/selector.js',
                                    'lib/jquery/src/traversing.js',
                                    'lib/jquery/src/manipulation.js',
                                    'lib/jquery/src/css.js',
                                    'lib/jquery/src/event-alias.js',
                                    'lib/jquery/src/ajax.js',
                                    'lib/jquery/src/ajax/script.js',
                                    'lib/jquery/src/ajax/jsonp.js',
                                    'lib/jquery/src/ajax/xhr.js',
                                    'lib/jquery/src/effects.js',
                                    'lib/jquery/src/offset.js',
                                    'lib/jquery/src/dimensions.js',
                                    'lib/jquery/src/deprecated.js',
                                    'lib/jquery/src/exports.js',
                                    'lib/jquery/src/outro.js'),
               'output_filename': ('lib/jquery.min.js')},
    'jquery-ui': {'source_filenames': ('lib/jquery-ui/ui/jquery.ui.core.js',
                                       'lib/jquery-ui/ui/jquery.ui.widget.js',
                                       'lib/jquery-ui/ui/jquery.ui.mouse.js',
                                       'lib/jquery-ui/ui/jquery.ui.draggable.js',
                                       'lib/jquery-ui/ui/jquery.ui.droppable.js',
                                       'lib/jquery-ui/ui/jquery.ui.resizable.js',
                                       'lib/jquery-ui/ui/jquery.ui.selectable.js',
                                       'lib/jquery-ui/ui/jquery.ui.sortable.js',
                                       'lib/jquery-ui/ui/jquery.ui.effect.js'),
                  'output_filename': ('lib/jquery-ui.min.js')},
    'jquery.collapsible': {'source_filenames': ('lib/jQuery-Collapsible-Content/js/jQuery.collapsible.js',),
                           'output_filename': ('lib/jquery.collapsible.min.js')},
    'jquery.cookie': {'source_filenames': ('lib/jquery-cookie/jquery.cookie.js',),
                      'output_filename': ('lib/jquery.cookie.min.js')},
    'jquery.dataTables': {'source_filenames': ('lib/DataTables/media/js/jquery.dataTables.js',),
                          'output_filename': ('lib/jquery.dataTables.min.js')},
    'openlayers': {'source_filenames': ('lib/openlayers/lib/OpenLayers/SingleFile.js',
                                        'lib/openlayers/lib/OpenLayers/Map.js',
                                        'lib/openlayers/lib/OpenLayers/Kinetic.js',
                                        'lib/openlayers/lib/OpenLayers/Projection.js',
                                        'lib/openlayers/lib/OpenLayers/Projection.js',
                                        'lib/openlayers/lib/OpenLayers/Layer/Vector.js',
                                        'lib/openlayers/lib/OpenLayers/Layer/OSM.js',
                                        'lib/openlayers/lib/OpenLayers/Layer/Bing.js',
                                        'lib/openlayers/lib/OpenLayers/Layer/WMS.js',
                                        'lib/openlayers/lib/OpenLayers/Layer/Google/v3.js',
                                        'lib/openlayers/lib/OpenLayers/Renderer/SVG.js',
                                        'lib/openlayers/lib/OpenLayers/Protocol/HTTP.js'),
                   'output_filename': ('lib/OpenLayers.min.js')},
}

PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.closure.ClosureCompressor'
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'


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
    "dataox.core.context_processors.base_template_chooser",
    "dataox.analytics.context_processors.do_not_track",
)

IMAGE_TYPES = ('foaf:Image',)

SOURCE_URL = 'https://source.data.ox.ac.uk/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'object_permissions.backend.ObjectPermBackend',
    'django_webauth.backends.webauth_ldap.WebauthLDAPBackend',
)

MIDDLEWARE_CLASSES = (
    'dataox.auth.middleware.AuthenticatedAsMiddleware',
    'django_hosts.middleware.HostsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'humfrey.base.middleware.AccessControlAllowOriginMiddleware',
#    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django_conneg.support.middleware.BasicAuthMiddleware',
    'humfrey.pingback.middleware.PingbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ENDPOINT_QUERY = 'http://localhost:3030/public/query'
ENDPOINT_GRAPH = 'http://localhost:3030/public/data'

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
DEFAULT_FROM_EMAIL = 'Open Data Service [staging] <opendata@oucs.ox.ac.uk>'
SERVER_EMAIL = 'Open Data Service Administrators [staging] <opendata-admin@maillist.ox.ac.uk>'

SERVER_EMAIL = 'opendata-admin@maillist.ox.ac.uk'

REDIS_PARAMS = {'host': 'localhost',
                'port': 6379}

TIME_SERIES_URI_BASE = "http://data.ox.ac.uk/id/time-series/"
TIME_SERIES_SERVER_ARGS = {'address': ('localhost', 4545),
                           'authkey': 'vee4pohCpai7aeRegaizo1EeaL9aengo'}
TIME_SERIES_PATH = '/srv/humfrey/dataox/time-series/'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

ID_MAPPING = (
    ('https://data.ox.ac.uk/id/', 'https://data.ox.ac.uk/doc/', True),
    ('http://oxpoints.oucs.ox.ac.uk/id/', 'https://data.ox.ac.uk/doc:oxpoints/', False),
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
    'timeseries': 'http://purl.org/NET/time-series/',
    'oxnotation': 'https://data.ox.ac.uk/id/notation/',
    'prog': 'http://purl.org/prog/',
    'oxcap': 'http://purl.ox.ac.uk/oxcap/ns/',
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
}

SMTP_HOST = 'smtp.ox.ac.uk'

THUMBNAIL_WIDTHS = (200, 220, 400)
THUMBNAIL_HEIGHTS = (120, 80,)

SESSION_COOKIE_SECURE = True

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
RESOURCE_REGISTRY = 'dataox.resource.resource_registry'

HUMFREY_FEEDS = {
    'organization': 'dataox.feeds.organization.OrganizationFeedView',
}

# Monkey patches

import sys
import rdflib
if map(int, rdflib.__version__.split('.')) < [3, 0, 0]:
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
    del sys, date, datetime, time, l, _XSD_NS

# http://bugs.python.org/issue9639 (Python 2.6.6 regression)

import urllib2

if sys.version_info[:2] == (2, 6) and sys.version_info[2] >= 6:
    def fixed_http_error_401(self, req, fp, code, msg, headers):
        url = req.get_full_url()
        response = self.http_error_auth_reqed('www-authenticate',
                                          url, req, headers)
        self.retried = 0
        return response

    urllib2.HTTPBasicAuthHandler.http_error_401 = fixed_http_error_401
del rdflib, sys, urllib2
