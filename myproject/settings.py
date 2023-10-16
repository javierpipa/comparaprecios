import os
import logging

from pathlib import Path
from django.conf import settings as django_settings
from django.utils.translation import gettext_lazy as _
from django.contrib.messages import constants as messages
from decouple import config
from logging.handlers import RotatingFileHandler
from django.utils.log import ServerFormatter, RequireDebugTrue, RequireDebugFalse, AdminEmailHandler


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(h$6-v$5wukt&o#k^27_y+7b9!mol%iqyh-t+z_@r%(1u*^9qs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False)
# DEBUG = True

ALLOWED_HOSTS = ['*']
DATA_UPLOAD_MAX_NUMBER_FIELDS = 29240
INTERNAL_IPS = [
    # ...
    '127.0.0.1', 'www.devop.cl'
    # ...
]

SITE_ID = 1

GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='valor_predeterminado')


INSTALLED_APPS = [
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.humanize",
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.redirects',
    'sekizai',
    'cms',
    'menus',
    'treebeard',
    'filer',
    'easy_thumbnails',
    'mptt',
    'djangocms_text_ckeditor',
    'djangocms_link',
    'djangocms_file',
    'djangocms_picture',
    'djangocms_video',
    'djangocms_googlemap',
    'djangocms_snippet',
    'djangocms_style',
    'djangocms_column',
    'djangocms_frontend',
    'djangocms_frontend.contrib.accordion',
    'djangocms_frontend.contrib.alert',
    'djangocms_frontend.contrib.badge',
    'djangocms_frontend.contrib.card',
    'djangocms_frontend.contrib.carousel',
    'djangocms_frontend.contrib.collapse',
    'djangocms_frontend.contrib.content',
    'djangocms_frontend.contrib.grid',
    'djangocms_frontend.contrib.jumbotron',
    'djangocms_frontend.contrib.link',
    'djangocms_frontend.contrib.listgroup',
    'djangocms_frontend.contrib.media',
    'djangocms_frontend.contrib.image',
    'djangocms_frontend.contrib.tabs',
    'djangocms_frontend.contrib.utilities',
    'django_celery_beat',
    'django_celery_results',

    'precios_integration',
    'precios',

    'members',
    'mathfilters',
    "rest_framework",

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'debug_toolbar',
    'django_extensions',

    'djangocms_blog',
    'aldryn_apphooks_config',
    'parler',
    'taggit',
    'taggit_autosuggest',
    'meta',
    'sortedm2m',
    'djangocms_maps',
    'djangocms_forms',
    "djangocms_page_meta",
    "djangocms_page_tags",
    'django_json_ld',
    'django_user_agents',
    'currencies',
    'django_prices_openexchangerates',
]

# django-json-ld
# JSON_LD_CONTEXT_ATTRIBUTE       = 'sd'
# JSON_LD_MODEL_ATTRIBUTE         = 'sd'
# JSON_LD_DEFAULT_CONTEXT         = 'https://schema.org/'
# JSON_LD_EMPTY_INPUT_RENDERING   = 'generate_thing'
# JSON_LD_DEFAULT_TYPE            = 'Thing'
# JSON_LD_INDENT                  = None
# JSON_LD_GENERATE_URL            = True


## openexchangerates
OPENEXCHANGERATES_APP_ID='64c3009ad5614988854aa3a17e2cd101'
OPENEXCHANGERATES_BASE_CURRENCY='CLP'
OPENEXCHANGERATES_API_KEY='64c3009ad5614988854aa3a17e2cd101'
## Taggit
TAGGIT_CASE_INSENSITIVE = True

## mttp
MPTT_ADMIN_LEVEL_INDENT = 20

# Google OAUTH
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
LOGIN_REDIRECT_URL = '/members/update_member/'
LOGOUT_REDIRECT_URL = '/'


###############

DJANGOCMS_FORMS_PLUGIN_MODULE = ('Generic')
DJANGOCMS_FORMS_PLUGIN_NAME = ('Form')
DJANGOCMS_FORMS_DEFAULT_TEMPLATE = 'djangocms_forms/form_template/default.html'
DJANGOCMS_FORMS_TEMPLATES = (
    ('forms1.html', ('Formularios')),
)


DJANGOCMS_FORMS_WIDGET_CSS_CLASSES = {'__all__': ('form-control', )}
DJANGOCMS_FORMS_USE_HTML5_REQUIRED = False
DJANGOCMS_FORMS_REDIRECT_DELAY = 10000  # 10 seconds
DJANGOCMS_FORMS_FORMAT_CHOICES = (
    ("csv", ("CSV")),
    ("json", ("JSON")),
    ("yaml", ("YAML")),
    ("xlsx", ("Microsoft Excel")),
)
TEMPLATE_DEBUG = DEBUG
DJANGOCMS_FORMS_RECAPTCHA_PUBLIC_KEY = '6Ld8ZYklAAAAAMg91paZAQRy1YL2ILwHHgdU-aBK'
DJANGOCMS_FORMS_RECAPTCHA_SECRET_KEY = '6Ld8ZYklAAAAAAKjaMvlRzRUACxlL7vDaCTTntly'


MAPS_PROVIDERS = [
    ('googlemaps', GOOGLE_API_KEY),
]


# Metas
META_USE_SITES = True
META_USE_OG_PROPERTIES = True
META_USE_TITLE_TAG = True
META_USE_FACEBOOK_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SCHEMAORG_PROPERTIES = True
META_USE_GOOGLEPLUS_PROPERTIES = True  # django-meta 1.x+

META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = 'devop.cl'
META_SITE_NAME = 'DEVOP'


# META_INCLUDE_KEYWORDS
# SITE_PROTOCOL = getattr(django_settings, "META_SITE_PROTOCOL", None)
# SITE_DOMAIN = getattr(django_settings, "META_SITE_DOMAIN", None)
# SITE_TYPE = getattr(django_settings, "META_SITE_TYPE", None)
# SITE_NAME = getattr(django_settings, "META_SITE_NAME", None)
# INCLUDE_KEYWORDS = getattr(django_settings, "META_INCLUDE_KEYWORDS", [])
# DEFAULT_KEYWORDS = getattr(django_settings, "META_DEFAULT_KEYWORDS", [])
# IMAGE_URL = getattr(django_settings, "META_IMAGE_URL", django_settings.STATIC_URL)
# USE_OG_PROPERTIES = getattr(django_settings, "META_USE_OG_PROPERTIES", False)
# USE_TWITTER_PROPERTIES = getattr(django_settings, "META_USE_TWITTER_PROPERTIES", False)
# USE_FACEBOOK_PROPERTIES = getattr(django_settings, "META_USE_FACEBOOK_PROPERTIES", False)
# USE_SCHEMAORG_PROPERTIES = getattr(django_settings, "META_USE_SCHEMAORG_PROPERTIES", False)
# USE_SITES = getattr(django_settings, "META_USE_SITES", False)
# USE_TITLE_TAG = getattr(django_settings, "META_USE_TITLE_TAG", False)
# OG_NAMESPACES = getattr(django_settings, "META_OG_NAMESPACES", None)

# print(SITE_PROTOCOL,SITE_DOMAIN, SITE_TYPE,  SITE_NAME, INCLUDE_KEYWORDS,DEFAULT_KEYWORDS )

OBJECT_TYPES = (
    ("Article", _("Article")),
    ("Website", _("Website")),
)
TWITTER_TYPES = (
    ("summary", _("Summary Card")),
    ("summary_large_image", _("Summary Card with Large Image")),
    ("product", _("Product")),
    ("photo", _("Photo")),
    ("player", _("Player")),
    ("app", _("App")),
)
FB_TYPES = OBJECT_TYPES
SCHEMAORG_TYPES = (
    ("Article", _("Article")),
    ("Blog", _("Blog")),
    ("WebPage", _("Page")),
    ("WebSite", _("WebSite")),
    ("Event", _("Event")),
    ("Product", _("Product")),
    ("Place", _("Place")),
    ("Person", _("Person")),
    ("Book", _("Book")),
    ("LocalBusiness", _("LocalBusiness")),
    ("Organization", _("Organization")),
    ("Review", _("Review")),
)

# OG_SECURE_URL_ITEMS = getattr(django_settings, "META_OG_SECURE_URL_ITEMS", ("image", "audio", "video"))
# DEFAULT_IMAGE = getattr(django_settings, "META_DEFAULT_IMAGE", "")
# DEFAULT_TYPE = getattr(django_settings, "META_SITE_TYPE", OBJECT_TYPES[0][0])
# FB_TYPE = getattr(django_settings, "META_FB_TYPE", OBJECT_TYPES[0][0])
# FB_TYPES = getattr(django_settings, "META_FB_TYPES", FB_TYPES)
# FB_APPID = getattr(django_settings, "META_FB_APPID", "")
# FB_PROFILE_ID = getattr(django_settings, "META_FB_PROFILE_ID", "")
# FB_PUBLISHER = getattr(django_settings, "META_FB_PUBLISHER", "")
# FB_AUTHOR_URL = getattr(django_settings, "META_FB_AUTHOR_URL", "")
# FB_PAGES = getattr(django_settings, "META_FB_PAGES", "")
# TWITTER_TYPE = getattr(django_settings, "META_TWITTER_TYPE", TWITTER_TYPES[0][0])
# TWITTER_TYPES = getattr(django_settings, "META_TWITTER_TYPES", TWITTER_TYPES)
# TWITTER_SITE = getattr(django_settings, "META_TWITTER_SITE", "")
# TWITTER_AUTHOR = getattr(django_settings, "META_TWITTER_AUTHOR", "")
# SCHEMAORG_TYPE = getattr(django_settings, "META_SCHEMAORG_TYPE", SCHEMAORG_TYPES[0][0])
# SCHEMAORG_TYPES = getattr(django_settings, "META_SCHEMAORG_TYPES", SCHEMAORG_TYPES)


# Metas
MIDDLEWARE = [
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['myproject/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'django.template.context_processors.i18n',
                'currencies.context_processors.currencies',
                # 'django.core.context_processors.request',
            ],
        },
    },
]
XTENSIONS_MAX_UNIQUE_QUERY_ATTEMPTS = 1

CMS_TEMPLATES = [
    ('home.html', 'Home page template'),
    ('index.html', 'Index'),
    ('fullwidth.html', 'Fullwidth'),
    ('bootstrap5.html', 'Bootstrap 5 Demo'),
    ('pagina_contenido.html', 'Contenido'),
]

WSGI_APPLICATION = 'myproject.wsgi.application'
X_FRAME_OPTIONS = 'SAMEORIGIN'

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'craw3_cms',
        'USER': 'root',
        'PASSWORD': 'dbrootdevel',
        'HOST': 'localhost',
        'PORT': 3306,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4'
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "craw3_cms"
    }
}

USER_AGENTS_CACHE = 'default'
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Celery
CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
BROKER_URL = 'amqp://crawler:crawlerpazz@localhost:5672/craw'
CELERY_BROKER_URL = 'amqp://crawler:crawlerpazz@localhost:5672/craw'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_DEFAULT_QUEUE = "craw_queu"
CELERY_DEFAULT_QUEUE = "craw_queu"
CELERY_DEFAULT_EXCHANGE = "craw_exchange"
CELERY_RESULT_BACKEND = "django-db"
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "America/Santiago"
CELERY_IGNORE_RESULT = False
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
CELERY_RESULT_EXPIRES = 150
CELERY_CREATE_MISSING_QUEUES = True

CELERY_FLOWER_USER = 'admin'
CELERY_FLOWER_PASSWORD = config('CELERY_FLOWER_PASSWORD', default='cps112233')

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DECIMAL_SEPARATOR = ','

LANGUAGE_CODE = 'es'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_ROOT = "static_root"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
LANGUAGES = [
    ('es', 'Spanish'),
]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


GOOGLE_ANALYTICS = {
    'google_analytics_id': 'G-WC6MSYJY1Q',
}


PARLER_LANGUAGES = {
    1: (
        {'code': 'es', },
    ),
    'default': {
        'fallbacks': ['es'],
    }
}

# #gmail_send/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'pijavier983@gmail.com'
EMAIL_HOST_PASSWORD = 'jybwrijkzlwhehbe'  # past the key or password app here
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'Javier Pi-DEVOP'


MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}
# LOGS
# Define folder a usar
log_folder = '/var/log/devop'

if not os.path.exists(log_folder):
    os.makedirs(log_folder)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'django.server': {
            '()': ServerFormatter,
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_true': {
            '()': RequireDebugTrue,
        },
        'require_debug_false': {
            '()': RequireDebugFalse,
        },
    },
    'handlers': {
        'request_handler': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            #            'filename': os.path.join(log_folder, 'request_log.log'),
            'filename': 'logs/request_log.log',

            'maxBytes': 1024 * 1024 * 5,  # 5Mb
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'default': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            #            'filename': os.path.join(log_folder, 'default_log.log'),
            'filename': 'logs/default_log.log',
            'maxBytes': 1024 * 1024 * 5,  # 5Mb
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'django.server': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            #            'filename': os.path.join(log_folder, 'devo_server_log.log'),
            'filename': 'logs/devo_server_log.log',
            'maxBytes': 1024 * 1024 * 5,  # 5Mb
            'backupCount': 5,
            'formatter': 'django.server'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'gunicorn': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            #            'filename': os.path.join(log_folder, 'gunicorn.errors.log'),
            'filename': 'logs/gunicorn.errors.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        }
    },
    'loggers': {
        'django': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['request_handler', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'gunicorn.errors': {
            'level': 'DEBUG',
            'handlers': ['gunicorn'],
            'propagate': True,
        },
    }
}
