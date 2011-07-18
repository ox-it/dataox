from __future__ import absolute_import
import os

from humfrey.settings.common import *

ENDPOINT_URL = 'http://localhost:3030/dataset/query'
GRAPH_URL = 'http://localhost:3030/dataset/data'
SERVED_DOMAINS = ('data.ox.ac.uk',)

INSTALLED_APPS += (
    'humfrey.dataox',
    'humfrey.pingback',
)

ROOT_URLCONF = 'humfrey.urls.dataox'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..', 'dataox', 'media')

MIDDLEWARE_CLASSES += (
    'humfrey.pingback.middleware.PingbackMiddleware',
)

CACHE_BACKEND = 'memcached://127.0.0.1:3031/'

EMAIL_HOST = 'smtp.ox.ac.uk'
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get('email', 'user')
EMAIL_HOST_PASSWORD = config.get('email', 'password')
SERVER_EMAIL = 'dataox@opendata.nsms.ox.ac.uk'
DEFAULT_FROM_EMAIL = 'opendata@oucs.ox.ac.uk'

RESIZED_IMAGE_CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'external_images')