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



ROOT_HOSTCONF = 'dataox.hosts'
DEFAULT_HOST = 'empty'

if STAGING:
    INSTALLED_APPS += ('dataox.staging',)
    MIDDLEWARE_CLASSES = ('dataox.staging.middleware.StagingMiddleware',) + MIDDLEWARE_CLASSES
    STATIC_URL = '/static.data.ox.ac.uk/'

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
ELASTICSEARCH_INDEXES = [
    {'id': 'college',
     'name': 'Colleges of the University of Oxford',
     'template_name': 'browse/list/college',
     'reindex_on_change': ['oxpoints'],
     'query': """SELECT ?uri (SAMPLE(?label_) as ?label) (SAMPLE(?homepage_) as ?homepage) (SAMPLE(?logo_) as ?logo) (SAMPLE(?depiction_) as ?depiction) WHERE {
                   ?uri a oxp:College ;
                     skos:prefLabel ?label_ .
                   OPTIONAL { ?uri foaf:homepage ?homepage_ } .
                   OPTIONAL { ?uri foaf:logo ?logo_ } .
                   OPTIONAL { ?uri foaf:depiction ?depiction_ }
                 } GROUP BY ?uri"""},
    {'id': 'unit',
     'name': 'Units of the University of Oxford',
     'template_name': 'browse/list/unit',
     'reindex_on_change': ['oxpoints'],
     'query': """SELECT ?uri (SAMPLE(?label_) as ?label) (SAMPLE(?homepage_) as ?homepage) (COALESCE(SAMPLE(?sortLabel_), SAMPLE(?label_)) as ?sortLabel) ?division ?division_label (SAMPLE(?oucs_) as ?oucs) (SAMPLE(?finance_) as ?finance) WHERE {
                   ?uri rdf:type/rdfs:subClassOf* oxp:Unit ;
                     skos:prefLabel ?label_ .
                   OPTIONAL { ?uri ov:sortLabel ?sortLabel_ } .
                   OPTIONAL { ?uri foaf:homepage ?homepage_ } .
                   OPTIONAL { ?uri oxp:hasOUCSCode ?oucs_ } .
                   OPTIONAL { ?uri oxp:hasFinanceCode ?finance_ } .
                   OPTIONAL { ?uri org:subOrganizationOf* ?division .
                              ?division a oxp:Division ;
                                skos:prefLabel ?division_label } .
                 } GROUP BY ?uri ?division ?division_label"""},
    {'id': 'current-vacancy',
     'name': 'Current vacancies',
     'template_name': 'browse/list/current-vacancy',
     'per_page': 50,
     'group': ['unit'],
     'reindex_on_change': ['oxpoints', 'vacancies'],
     'query': """SELECT ?uri ?label ?unit ?unit_label ?salary ?description ?opening ?closing WHERE {
                   GRAPH <http://data.ox.ac.uk/graph/vacancies/current> {
                   ?uri a vacancy:Vacancy ;
                     rdfs:label ?label ;
                     vacancy:applicationClosingDate ?closing .
                   } .
                   FILTER (?closing > now()) .
                   OPTIONAL { ?uri vacancy:organizationalUnit ?unit . ?unit skos:prefLabel ?unit_label } .
                   OPTIONAL { ?uri vacancy:salary/rdfs:label ?salary } .
                   OPTIONAL { ?uri rdfs:comment ?description } .
                   OPTIONAL { ?uri vacancy:applicationOpeningDate ?opening } .
                   ?uri vacancy:applicationClosingDate ?closing
                   FILTER ( datatype(?description) != xtypes:Fragment-XHTML ) .
                 } ORDER BY ?label ?uri"""},
    {'id': 'building',
     'name': 'Buildings',
     'template_name': 'browse/list/building',
     'per_page': 50,
     'group': ['occupant', 'depiction'],
     'reindex_on_change': ['oxpoints'],
     'query': """SELECT ?uri ?label ?long ?lat ?extendedAddress ?streetAddress ?locality ?postalCode ?estates ?occupant ?occupant_label ?depiction WHERE {
                   ?uri a oxp:Building ;
                     skos:prefLabel ?label .
                   OPTIONAL { ?uri geo:long ?long ; geo:lat ?lat } .
                   OPTIONAL { ?uri oxp:hasOBNCode ?estates } .
                   OPTIONAL { ?occupant org:hasSite ?uri ; skos:prefLabel ?occupant_label } .
                   OPTIONAL { ?uri foaf:depiction ?depiction } .
                   OPTIONAL { ?uri v:adr ?adr .
                                OPTIONAL { ?adr v:extended-address ?extendedAddress } .
                                OPTIONAL { ?adr v:street-address ?streetAddress } .
                                OPTIONAL { ?adr v:locality ?locality } .
                                OPTIONAL { ?adr v:postal-code ?postalCode } } .
                 } ORDER BY ?label ?uri"""},
    {'id': 'electricity-meter',
     'name': 'Electricity meters',
     'template_name': 'browse/list/meter',
     'per_page': 100,
     'group': ['place', 'include', 'exclude'],
     'reindex_on_change': ['oxpoints', 'openmeters'],
     'query': """SELECT ?uri ?type ?meterPoint ?label ?place ?place_label ?place_lat ?place_long ?place_type ?seriesName ?include ?include_seriesName ?exclude ?exclude_seriesName ?endpoint WHERE {
                   ?uri a ?type ; timeseries:endpoint ?endpoint .
                   FILTER (?type in (timeseries:TimeSeries, timeseries:VirtualTimeSeries)) .
                   ?meterPoint timeseries:timeSeries ?uri .
                   OPTIONAL { ?meterPoint rdfs:label ?label } .
                   OPTIONAL { ?uri timeseries:seriesName ?seriesName } .
                   OPTIONAL { ?uri timeseries:include ?include . ?include timeseries:seriesName ?include_seriesName } .
                   OPTIONAL { ?uri timeseries:exclude ?exclude . ?exclude timeseries:seriesName ?exclude_seriesName } .
                   OPTIONAL { ?meterPoint meter:pertainsTo ?place .
                              ?place a ?place_type ;
                                 skos:prefLabel ?place_label .
                              OPTIONAL { ?place geo:lat ?place_lat ;
                                           geo:long ?place_long } }
                 }"""},
]

UPDATE_FILES_DIRECTORY = os.path.join(MEDIA_ROOT, 'update-files')

if config.get('ckan:enabled') == 'true':
    CKAN_PATTERNS = {'name': 'ox-ac-uk-%s',
                     'title': '%s (University of Oxford)',
                     'author': '%s, University of Oxford',
                     'maintainer': '%s, University of Oxford'}
    CKAN_GROUPS |= set(['university-of-oxford'])
    CKAN_TAGS |= set(['oxford', 'university'])

ARCHIVE_PATH = relative_path(config.get('archive:path'))

LOGIN_URL = '//admin.data.ox.ac.uk/login/'
LOGOUT_URL = '//admin.data.ox.ac.uk/logout/'
LOGIN_REDIRECT_URL = '//admin.data.ox.ac.uk/'
SESSION_COOKIE_SECURE = not DEBUG

VOCABULARY_URL_OVERRIDES = {
    'oxp': 'http://oxpoints.oucs.ox.ac.uk/ns.ttl',
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "dataox.core.context_processors.base_template_chooser"
)
