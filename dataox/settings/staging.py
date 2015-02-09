from dataox.settings.base import *

DEBUG = False
STAGING = True

INSTALLED_APPS += (
    'dataox.staging',
)

DEFAULT_HOST = 'staging'

STATIC_URL = '/static.data.ox.ac.uk/'

TEMPLATE_CONTEXT_PROCESSORS += (
    'dataox.staging.context_processors.staging',
)

MIDDLEWARE_CLASSES = (
    'dataox.staging.middleware.StagingMiddleware',
) + MIDDLEWARE_CLASSES

SERVER_EMAIL = 'Open Data Service Administrators [staging] <opendata-admin@maillist.ox.ac.uk>'