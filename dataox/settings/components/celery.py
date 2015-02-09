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
