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
    'humfrey.update',
    'humfrey.graphviz',
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
})
