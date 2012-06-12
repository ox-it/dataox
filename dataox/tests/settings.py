import atexit
import imp
import os
import shutil
import tempfile

DEBUG = False
TESTING = True

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_conneg',
    'django_hosts',
    'django_jenkins',
    'django_webauth',
    'humfrey.base',
    'humfrey.desc',
    'humfrey.elasticsearch',
    'humfrey.graphviz',
    'humfrey.linkeddata',
    'humfrey.sparql',
    'humfrey.streaming',
    'humfrey.results',
    'humfrey.update',
    'object_permissions',
    'openorg_timeseries',
    'dataox.core',
    'dataox.course',
    'dataox.equipment',
)

ROOT_HOSTCONF = 'dataox.hosts'
ROOT_URLCONF = 'dataox.urls.empty'
DEFAULT_HOST = 'empty'

IGNORE_TEST_MODULES = [
    'openorg_timeseries.tests.admin',
    'humfrey.desc.tests',
    'humfrey.linkeddata.tests',
    'django_hosts.tests',
    'object_permissions.tests',
    'django.contrib.auth.tests.remote_user',
]

TEST_RUNNER = 'humfrey.tests.runners.HumfreyTestSuiteRunner'

try:
    imp.find_module('django_jenkins')
except ImportError:
    pass
else:
    INSTALLED_APPS += ('django_jenkins',)

    JENKINS_TEST_RUNNER = 'humfrey.tests.runners.HumfreyJenkinsTestSuiteRunner'
    JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                     'django_jenkins.tasks.with_coverage',
                     'django_jenkins.tasks.django_tests',
                     'django_jenkins.tasks.run_pep8',
                     'django_jenkins.tasks.run_pyflakes')

TEST_URI = 'http://data.example.com/id/Foo'
TEST_DOMAIN = 'data.ox.ac.uk'

EXTRA_TEST_MODULES = ('dataox.datasets.vacancies.tests',)

ENDPOINT_QUERY = None

MIDDLEWARE_CLASSES = ()

# This stuff will all be wiped out when the tests are finished.

TEMP_DIRECTORY = tempfile.mkdtemp()
@atexit.register
def remove_temp_directory():
    shutil.rmtree(TEMP_DIRECTORY)

MEDIA_ROOT = os.path.join(TEMP_DIRECTORY, 'media')
UPDATE_FILES_DIRECTORY = os.path.join(MEDIA_ROOT, 'update-files')
TIME_SERIES_PATH = os.path.join(TEMP_DIRECTORY, 'time-series')

_directories_to_create = [
    MEDIA_ROOT,
    UPDATE_FILES_DIRECTORY,
    TIME_SERIES_PATH,
]

for x in _directories_to_create:
    if not os.path.exists(x):
        os.makedirs(x)

del _directories_to_create, x, remove_temp_directory

