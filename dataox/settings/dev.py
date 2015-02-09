from dataox.settings.staging import *

import os

DEBUG = True
STAGING = True

DOWNLOAD_CACHE = os.path.join(os.path.dirname(__file__),
                                      'download-cache')

IMAGE_CACHE_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                     'image-cache')

SOURCE_DIRECTORY = os.path.join(os.path.dirname(__file__),
                                'source-data')

STATIC_ROOT = os.path.join(os.path.dirname(__file__),
                           'static-collected')

SESSION_COOKIE_SECURE = False
