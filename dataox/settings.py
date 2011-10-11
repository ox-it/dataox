from __future__ import absolute_import

import imp
import os

from humfrey.settings.common import *

ENDPOINT_URL = 'http://localhost:3030/dataset/query'
GRAPH_URL = 'http://localhost:3030/dataset/data'
SERVED_DOMAINS = ('data.ox.ac.uk',)

INSTALLED_APPS += (
    'humfrey.longliving',
    'dataox.core',
    'dataox.resource',
    'dataox.feeds',
    'humfrey.update',
    'humfrey.graphviz',
    'humfrey.browse',
    'openorg_timeseries',
)

ADMINS = (
    (config.get('admin:name'), config.get('admin:email')),
)

ROOT_URLCONF = 'dataox.urls.empty'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

MEDIA_URL = 'http://data.ox.ac.uk/site-media/'

ROOT_HOSTCONF = 'dataox.hosts'
DEFAULT_HOST = 'empty'

CACHE_BACKEND = 'memcached://127.0.0.1:3031/'

EMAIL_HOST = 'smtp.ox.ac.uk'
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get('email', 'user')
EMAIL_HOST_PASSWORD = config.get('email', 'password')
SERVER_EMAIL = 'dataox@opendata.nsms.ox.ac.uk'
DEFAULT_FROM_EMAIL = 'opendata@oucs.ox.ac.uk'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
) + TEMPLATE_DIRS

THUMBNAIL_WIDTHS = (200, 400)
THUMBNAIL_HEIGHTS = (80,)

ID_MAPPING = (
    ('http://data.ox.ac.uk/id/', 'http://data.ox.ac.uk/doc/', True),
    ('http://oxpoints.oucs.ox.ac.uk/id/', 'http://data.ox.ac.uk/doc:oxpoints/', False),
)

UPDATE_DEFINITION_DIRECTORIES += (
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'datasets')),
)
if 'update:definitions' in config:
    UPDATE_DEFINITION_DIRECTORIES += (relative_path(config['update:definitions']),)

TIME_SERIES_URI_BASE = "http://data.ox.ac.uk/id/time-series/"
TIME_SERIES_PORT = 4545
TIME_SERIES_PATH = relative_path(config.get('timeseries:path'))

LONGLIVING_CLASSES.add('openorg_timeseries.longliving.rrdtool.RRDThread')

SOURCE_DIRECTORY = relative_path(config.get('update:source_directory'))

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

ADDITIONAL_NAMESPACES.update({
    'vacancy': 'http://purl.org/openorg/vacancy/',
    'salary': 'http://purl.org/openorg/salary/',
    'meter': 'http://purl.org/meter/',
    'timeseries': 'http://purl.org/NET/time-series/',

})

BROWSE_LISTS = [
    {'id': 'college',
     'name': 'Colleges of the University of Oxford',
     'template_name': 'browse/list/college',
     'initial_sort': 'label',
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
     'initial_sort': 'sortLabel',
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
     'initial_sort': 'label',
     'per_page': 50,
     'group': ['unit'],
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
     'initial_sort': 'label',
     'per_page': 50,
     'group': ['occupant', 'depiction'],
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
     'initial_sort': 'label',
     'per_page': 100,
     'group': ['place', 'include', 'exclude'],
     'query': """SELECT ?uri ?type ?meterPoint ?label ?place ?place_label ?place_lat ?place_long ?place_type ?seriesName ?include ?include_seriesName ?exclude ?exclude_seriesName WHERE {
                   ?uri a ?type .
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
