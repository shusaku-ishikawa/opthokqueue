from .base import *

ALLOWED_HOSTS = ["opthok-navi.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'queue',
        'USER': 'root',
        'PASSWORD': '332191-Aa',
        'HOST': '127.0.0.1',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# JOBs
CRONJOBS = [
    ('* * * * *', 'django.core.management.call_command', ['reply_emails']),
]
CRONTAB_LOCK_JOBS = False

DEFAULT_CHARSET = 'utf-8'
EMAIL_HOST = 'opthok-navi.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@opthok-navi.com'
EMAIL_HOST_PASSWORD = 'P@ssw0rd'
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = 'おぷきた連絡ナビ <noreply@opthok-navi.com>'
DEFAULT_FROM_EMAIL_FOR_QR = 'noreply@opthok-navi.com'


