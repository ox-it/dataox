from .settings_staging import *

import os

DEBUG = True

SECRET_KEY = 'lOd5P3JpSi6hA3cxpJSLbQhngcJknlhXfrxoxNbFlf6X3YNEagAIfXz5ASRDGEQR'

DOWNLOAD_CACHE = os.path.join(os.path.dirname(__file__),
                                      'download-cache')

IMAGE_CACHE_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                     'image-cache')

SOURCE_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                'source-data')

STATIC_ROOT = os.path.join(os.path.dirname(__file__),
                           'static-collected')

PIPELINE_CLOSURE_BINARY = '/home/alex/src/closure/compiler'

STATIC_URL = '//localhost:8001/'
