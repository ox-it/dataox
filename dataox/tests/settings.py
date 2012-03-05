import os

os.environ['HUMFREY_CONFIG_FILE'] = os.path.join(os.path.dirname(__file__), 'data', 'config.ini')

from dataox.settings import *

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

INSTALLED_APPS += (
    'django_jenkins',
    'humfrey.elasticsearch',
)

JENKINS_TEST_RUNNER = 'humfrey.tests.HumfreyJenkinsTestSuiteRunner'
JENKINS_TASKS = ('django_jenkins.tasks.run_pylint',
                 'django_jenkins.tasks.with_coverage',
                 'django_jenkins.tasks.django_tests',
                 'django_jenkins.tasks.run_pep8',
                 'django_jenkins.tasks.run_pyflakes')
PROJECT_APPS = tuple(app for app in INSTALLED_APPS if app.startswith('humfrey.'))

TEST_URI = 'http://data.example.com/id/Foo'
TEST_DOMAIN = 'data.ox.ac.uk'

EXTRA_TEST_MODULES = ('dataox.datasets.vacancies.tests',
                      )
