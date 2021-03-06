"""
Glossary of settings/prod.py:

- Hosting + Authentication
- Email
- SSL Security
- Installed applications
- Database
- Templates
- HTML minification
- Cache
- Staticfiles
- Logging
"""

from .common import *
import datetime
import dj_database_url


############################
# HOSTING + AUTHENTICATION #
############################
ADMINS = (
    # Uncomment lines below if you want emails about server errors.
    # ("Kirk Sanderson", "kirksanderson1@gmail.com"),
    ("JP Halis", "jphalisnj@gmail.com"),
)
MANAGERS = ADMINS
FULL_DOMAIN = 'knoblinx.com'
HEROKU_DOMAIN = 'knoblinx.herokuapp.com'
ALLOWED_HOSTS = [
    '127.0.0.1',

    HEROKU_DOMAIN,
    '*{}'.format(HEROKU_DOMAIN),
    '*.{}'.format(HEROKU_DOMAIN),
    'wwww.{}'.format(HEROKU_DOMAIN),

    FULL_DOMAIN,
    '*{}'.format(FULL_DOMAIN),
    '*.{}'.format(FULL_DOMAIN),
    'wwww.{}'.format(FULL_DOMAIN),
]


#########
# EMAIL #
#########
DEFAULT_FROM_EMAIL = 'noreply.knoblinx@gmail.com'
DEFAULT_HR_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL
EMAIL_HOST_PASSWORD = 'KnobLinx1'
EMAIL_PORT = 587


################
# SSL SECURITY #
################
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_SECONDS = 0
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_HOST = None
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


##########################
# INSTALLED APPLICATIONS #
##########################
INSTALLED_APPS += (
    'storages',
)


############
# DATABASE #
############
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    }
}
DATABASES['default'].update(dj_database_url.config())  # For Heroku only


#############
# TEMPLATES #
#############
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join('templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]


#####################
# HTML MINIFICATION #
#####################
# KEEP_COMMENTS_ON_MINIFYING = False
# EXCLUDE_FROM_MINIFYING = ('^hidden/secure/{}/admin/'.format(APP_NAME),)


#########
# CACHE #
#########
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': [
#             '127.0.0.1:11211',
#         ],
#         'TIMEOUT': 60,
#         'OPTIONS': {
#             'MAX_ENTRIES': 1000
#         }
#     }
# }
# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 12
# CACHE_MIDDLEWARE_KEY_PREFIX = ''


###############
# STATICFILES #
###############
USING_S3 = True
USING_CLOUDFRONT = False
USING_EC2 = False

if USING_S3:
    AWS_ACCESS_KEY_ID = 'AKIAJI2UXLQ5CKQ6BFFQ'
    AWS_SECRET_ACCESS_KEY = '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'
    AWS_STORAGE_BUCKET_NAME = 'knoblinx-1'
    AWS_AUTO_CREATE_BUCKET = False
    AWS_S3_REGION_NAME = 'us-east-1'

    AWS_QUERYSTRING_AUTH = False
    AWS_QUERYSTRING_EXPIRE = 3600
    AWS_FILE_EXPIRE = 200
    AWS_PRELOAD_METADATA = True
    AWS_S3_ENCRYPTION = False
    AWS_S3_USE_SSL = True
    AWS_S3_SECURE_URLS = True
    AWS_S3_FILE_OVERWRITE = True
    AWS_S3_ENDPOINT_URL = None

    STATICFILES_STORAGE = '{}.s3utils.StaticS3BotoStorage'.format(APP_NAME)
    STATIC_S3_PATH = 'media/'
    DEFAULT_FILE_STORAGE = '{}.s3utils.MediaS3BotoStorage'.format(APP_NAME)
    DEFAULT_S3_PATH = 'static/'
    S3_URL = '//s3.amazonaws.com/{}/'.format(AWS_STORAGE_BUCKET_NAME)
    MEDIA_URL = S3_URL + STATIC_S3_PATH
    STATIC_URL = S3_URL + DEFAULT_S3_PATH

    if USING_CLOUDFRONT:
        AWS_CLOUDFRONT_DOMAIN = ''
        MEDIA_URL = '//{0}/{1}'.format(AWS_CLOUDFRONT_DOMAIN, STATIC_S3_PATH)
        STATIC_URL = '//{0}/{1}'.format(AWS_CLOUDFRONT_DOMAIN, DEFAULT_S3_PATH)
    elif USING_EC2:
        MEDIA_ROOT = '/home/ubuntu/{0}/{1}/media'.format(
            FULL_DOMAIN, APP_NAME)
        STATIC_ROOT = '/home/ubuntu/{0}/{1}/static/static'.format(
            FULL_DOMAIN, APP_NAME)

    two_months = datetime.timedelta(days=61)
    two_months_later = datetime.date.today() + two_months
    AWS_HEADERS = {
        'Expires': two_months_later.strftime('%A, %d %B %Y 20:00:00 EST'),
        'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
    }


###########
# LOGGING #
###########
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}
