"""
Django settings for benchmark project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

#import djcelery

from environ import Path
from benchmark.utils.environ import Env

ROOT_DIR = Path(__file__) - 3  # Three folders back

APPS_DIR = ROOT_DIR.path('benchmark')

# Nothing initially
env = Env()

# Read .env file
env_file = str(ROOT_DIR.path('.env'))
env.read_env(env_file)

SITE_ROOT = ROOT_DIR()

SITE_ID = env('SITE_ID', default=1)

DEBUG = env.bool('DJANGO_DEBUG', False)

# codeontap environment variables
BUILD_REFERENCE = env("BUILD_REFERENCE", default=None)
CONFIGURATION_REFERENCE = env("CONFIGURATION_REFERENCE", default=None)
APP_REFERENCE = env("APP_REFERENCE", default=None)
ENVIRONMENT = env("ENVIRONMENT", default='local')

if DEBUG:
    # require it only for debug=False, let user ignore it for debug=True
    SECRET_KEY = env('DJANGO_SECRET_KEY', default='XXX')
else:
    SECRET_KEY = env('DJANGO_SECRET_KEY')

# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = env(
    'DJANGO_ALLOWED_HOSTS',
    default='*'
).split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    #'django_ses',
    #'djcelery',
    'djcelery_email',
    'queued_storage',
    'memoize',
    'avatar'
]

LOCAL_APPS = [
    'benchmark',
    'benchmark.account',
    'benchmark.report',
    'benchmark.chart'
]

# Applications definition
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'benchmark.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'benchmark.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DATABASE_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env('DATABASE_NAME', default=''),
        'USER': env('DATABASE_USERNAME', default=''),
        'PASSWORD': env('DATABASE_PASSWORD', default=''),
        'HOST': env('DATABASE_HOST', default=''),
        'PORT': env('DATABASE_PORT', default='')
    }
}

# The age of session cookies, in seconds
SESSION_COOKIE_AGE = env.int('SESSION_COOKIE_AGE', default=60 * 60)

# Caching
DATA_SCIENCE_CACHE_BACKEND = env("DATA_SCIENCE_CACHE_BACKEND", default='django_redis.cache.RedisCache')
DATA_SCIENCE_CACHE_URL = env("DATA_SCIENCE_CACHE_URL", default='')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'releases': {
        'BACKEND': DATA_SCIENCE_CACHE_BACKEND,
        'LOCATION': DATA_SCIENCE_CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': None # Never expires
    },
    'charts': {
        'BACKEND': DATA_SCIENCE_CACHE_BACKEND,
        'LOCATION': DATA_SCIENCE_CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': SESSION_COOKIE_AGE * 2 # Expire it with session * 2
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

if DEBUG is False:
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
else:
    AUTH_PASSWORD_VALIDATORS = []  # hate it locally


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Canberra'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis')
#CELERYBEAT_SCHEDULER = env('CELERYBEAT_SCHEDULER', default='djcelery.schedulers.DatabaseScheduler')

#djcelery.setup_loader()

# AWS
AWS_REGION = env("AWS_REGION", default='')
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default='')
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default='')

# Emails
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='djcelery_email.backends.CeleryEmailBackend')
CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = env('SMTP_USE_TLS', default=True)
EMAIL_HOST = env('SMTP_HOST', default='')
EMAIL_PORT = env('SMTP_PORT', default=587)
EMAIL_HOST_USER = env('SMTP_USERNAME', default='')
EMAIL_HOST_PASSWORD = env('SMTP_PASSWORD', default='')
EMAIL_FROM_EMAIL = env('SMTP_FROM_EMAIL', default='')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env(
    "DJANGO_STATIC_ROOT",
    default=str(ROOT_DIR('../var/static_root'))
)

STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# AWS S3
AWS_REGION = env("AWS_REGION", default='')

APPDATA_BUCKET = env("APPDATA_BUCKET", default='')
APPDATA_PREFIX = env("APPDATA_PREFIX", default='')

AWS_STORAGE_BUCKET_NAME = APPDATA_BUCKET

AWS_UPLOADS_LOCATION = env("AWS_UPLOADS_LOCATION", default='uploads')
AWS_RELEASE_LOCATION = env("AWS_RELEASE_LOCATION", default='releases')

# TODO: Refactor it to use storage.remote_options
AWS_LOCATION = '{}/{}'.format(APPDATA_PREFIX, AWS_UPLOADS_LOCATION) if APPDATA_PREFIX else AWS_UPLOADS_LOCATION
AWS_RELEASE_LOCATION = '{}/{}'.format(APPDATA_PREFIX, AWS_RELEASE_LOCATION) if APPDATA_PREFIX else AWS_RELEASE_LOCATION

AWS_RELEASE_MANIFEST = '{}/manifest.json'.format(AWS_RELEASE_LOCATION)
S3_URL = 'http://{}.s3.amazonaws.com'.format(APPDATA_BUCKET)


#DEFAULT_FILE_STORAGE = 'benchmark.utils.s3.MediaS3BotoStorage'
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default='')
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default='')

AWS_S3_REGION_NAME = AWS_REGION

AWS_S3_OBJECT_PARAMETERS = {
    'ACL': 'bucket-owner-full-control'
}

AWS_DEFAULT_ACL = 'bucket-owner-full-control'

AWS_BUCKET_ACL = 'bucket-owner-full-control'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = str(ROOT_DIR('media'))

# Configuration for apps
FIXTURE_DIRS = (
    str(ROOT_DIR('fixtures')),
)

# New users activation signing salt
ACCOUNT_ACTIVATION_SALT = SECRET_KEY

# New users activation period
ACCOUNT_ACTIVATION_DAYS = 7

CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGIN_URL = '/account/login/'
# Redirect to page after login
LOGIN_REDIRECT_URL = '/'

# if we have sentry credentials - use it
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    INSTALLED_APPS += [
        'raven.contrib.django.raven_compat',
    ]
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': APP_REFERENCE,
        'environment': ENVIRONMENT
    }
