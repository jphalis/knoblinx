"""
Glossary of settings/common.py:

- Hosting + Authentication
- Email
- Internationalization
- Installed applications
- Middleware
- Password validation
- Templates
- Sessions
- File uploads
"""

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


############################
# HOSTING + AUTHENTICATION #
############################
SECRET_KEY = '=8t_p!l^8cllm-q)=ikxsyqyhu1%0651)!7=@g4p8qm6vg0&c0'
LOGIN_URL = "/auth/authenticate/"
AUTH_USER_MODEL = 'accounts.MyUser'
APP_NAME = 'knoblinx'


#########
# EMAIL #
#########
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None


########################
# INTERNATIONALIZATION #
########################
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
USE_TZ = False


##########################
# INSTALLED APPLICATIONS #
##########################
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'widget_tweaks',

    'accounts',
    'activity',
    'authentication',
    'core',
    'jobs',
    'search',
)


ROOT_URLCONF = '{}.urls'.format(APP_NAME)
WSGI_APPLICATION = '{}.wsgi.application'.format(APP_NAME)


MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    # 'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    # 'htmlmin.middleware.MarkRequestMiddleware',
)


#######################
# PASSWORD VALIDATION #
#######################
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


#############
# TEMPLATES #
#############
CRISPY_TEMPLATE_PACK = "bootstrap3"
HTML_MINIFY = True


############
# SESSIONS #
############
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 4 * 3  # three months
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


###############
# STATICFILES #
###############
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '..', 'static', 'static_dirs'),
)
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static', 'static')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')
MEDIA_URL = '/media/'


################
# FILE UPLOADS #
################
FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
