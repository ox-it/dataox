import os

EMAIL_HOST = os.environ['SMTP_SERVER']
EMAIL_PORT = 587

EMAIL_SUBJECT_PREFIX = '[dataox] '
DEFAULT_FROM_EMAIL = os.environ['FROM_ADDRESS']
SERVER_EMAIL = os.environ['FROM_ADDRESS']

del os
