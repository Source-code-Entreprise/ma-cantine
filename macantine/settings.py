"""
Django settings for macantine project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import sys
from pathlib import Path
import dotenv  # noqa

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET")
SECURE_SSL_REDIRECT = os.getenv("FORCE_HTTPS") == "True"

# The site uses http or https?
SECURE = os.getenv("SECURE") == "True"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") == "True"
AUTH_USER_MODEL = "data.User"
AUTHENTICATION_BACKENDS = ["macantine.backends.EmailUsernameBackend"]
ALLOWED_HOSTS = [x.strip() for x in os.getenv("ALLOWED_HOSTS").split(",")]

DEBUG_PERFORMANCE = os.getenv("DEBUG") == "True" and os.getenv("DEBUG_PERFORMANCE") == "True"

# Environment

ENVIRONMENT = os.getenv("ENVIRONMENT")

# Sentry
# No need making this one secret: https://forum.sentry.io/t/dsn-private-public/6297/3
if not DEBUG:
    sentry_sdk.init(
        dsn="https://5bbe469c02b341c7ae1b85e280e28b15@o548798.ingest.sentry.io/5795837",
        integrations=[DjangoIntegration()],
        traces_sample_rate=0,
        send_default_pii=False,
        send_client_reports=False,
    )

INTERNAL_IPS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
    "webpack_loader",
    "rest_framework",
    "ckeditor",
    "ckeditor_uploader",
    "macantine",
    "data",
    "api",
    "web",
    "magicauth",
    "django_filters",
    "common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "csp.middleware.CSPMiddleware",
]
CSRF_COOKIE_NAME = "csrftoken"
ROOT_URLCONF = "macantine.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "macantine.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": os.getenv("DB_USER"),
        "NAME": os.getenv("DB_NAME"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "CONN_MAX_AGE": 60,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Media and file storage
AWS_ACCESS_KEY_ID = os.getenv("CELLAR_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("CELLAR_SECRET")
AWS_S3_ENDPOINT_URL = os.getenv("CELLAR_HOST")
AWS_STORAGE_BUCKET_NAME = os.getenv("CELLAR_BUCKET_NAME")
AWS_LOCATION = "media"
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = os.getenv("DEFAULT_FILE_STORAGE")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", os.path.join(BASE_DIR, "media"))
MEDIA_URL = "/media/"

STATICFILES_STORAGE = os.getenv("STATICFILES_STORAGE")
SESSION_COOKIE_AGE = 31536000
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/s-identifier"

HOSTNAME = os.getenv("HOSTNAME")

# API - Django Rest Framework

REST_FRAMEWORK = {
    "COERCE_DECIMAL_TO_STRING": False,
    "UPLOADED_FILES_USE_URL": True,
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
}

# Frontend - VueJS application

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "frontend/dist/")]
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": DEBUG,
        "BUNDLE_DIR_NAME": "/bundles/",
        "STATS_FILE": os.path.join(FRONTEND_DIR, "webpack-stats.json"),
    }
}

# Email
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL")
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")

if DEBUG and EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025

ANYMAIL = {
    "SENDINBLUE_API_KEY": os.getenv("SENDINBLUE_API_KEY", ""),
}
NEWSLETTER_SENDINBLUE_LIST_ID = os.getenv("NEWSLETTER_SENDINBLUE_LIST_ID")

# Trello
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_API_TOKEN = os.getenv("TRELLO_API_TOKEN")
TRELLO_LIST_ID_CONTACT = os.getenv("TRELLO_LIST_ID_CONTACT")
TRELLO_LIST_ID_PUBLICATION = os.getenv("TRELLO_LIST_ID_PUBLICATION")

# Magicauth
MAGICAUTH_EMAIL_FIELD = "email"
MAGICAUTH_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
MAGICAUTH_LOGIN_URL = "envoyer-email-conexion"
MAGICAUTH_LOGGED_IN_REDIRECT_URL_NAME = "app"
MAGICAUTH_EMAIL_SUBJECT = "Votre lien de connexion avec Ma Cantine"
MAGICAUTH_EMAIL_HTML_TEMPLATE = "magicauth/magicauth_email.html"
MAGICAUTH_EMAIL_TEXT_TEMPLATE = "magicauth/magicauth_email.txt"
MAGICAUTH_LOGIN_VIEW_TEMPLATE = "magicauth/login_magicauth.html"
MAGICAUTH_EMAIL_SENT_VIEW_TEMPLATE = "magicauth/magicauth_email_sent.html"
MAGICAUTH_ENABLE_2FA = False

# CK Editor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Format", "Blockquote"],
            ["Bold", "Italic"],
            [
                "NumberedList",
                "BulletedList",
                "-",
                "Outdent",
                "Indent",
            ],
            ["Link", "Unlink"],
            [
                "Image",
                "-",
                "Table",
                "SpecialChar",
            ],
            ["Source", "Maximize"],
        ],
        "extraPlugins": ",".join(
            [
                "image2",
                "codesnippet",
                "placeholder",
            ]
        ),
        "removePlugins": ",".join(["image"]),
    }
}

# Analytics
MATOMO_ID = os.getenv("MATOMO_ID", "")

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Performance debug with Django debug console
if DEBUG_PERFORMANCE:
    INTERNAL_IPS.append("127.0.0.1")
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

# Maximum CSV import file size: 10Mo
CSV_IMPORT_MAX_SIZE = 10485760

PIPEDRIVE_API_TOKEN = os.getenv("PIPEDRIVE_API_TOKEN", None)

# CSP headers (https://content-security-policy.com/)

# CSP Debug domains -  unsfae-eval needed in DEBUG for hot-reload of the frontend server
CSP_DEBUG_DOMAINS = (
    "'unsafe-eval'",
    "localhost:*",
    "0.0.0.0:*",
    "127.0.0.1:*",
    "www.ssa.gov",  # for a11y testing with ANDI
    "ajax.googleapis.com",  # for a11y testing with ANDI
)

# CSP Default policy for resources such as JS, CSS, AJAX, etc. Note that not all directives fallback to this.
CSP_DEFAULT_SRC = ("'self'",)
if DEBUG:
    CSP_DEFAULT_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources of stylesheets or CSS
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
)
if DEBUG:
    CSP_STYLE_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources of Javascript
CSP_SCRIPT_SRC = (
    "'self'",
    "stats.data.gouv.fr",
    "'unsafe-inline'",
)
if DEBUG:
    CSP_SCRIPT_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources of images
CSP_IMG_SRC = (
    "'self'",
    "cellar-c2.services.clever-cloud.com",
    "voxusagers.numerique.gouv.fr",
    "'unsafe-inline'",
    "stats.data.gouv.fr",
    "www.w3.org",
    "data:",
)
if DEBUG:
    CSP_IMG_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources of fonts
CSP_FONT_SRC = ("'self'",)
if DEBUG:
    CSP_IMG_SRC += CSP_FONT_SRC

# CSP valid sources of AJAX, WebSockets, EventSources, etc
CSP_CONNECT_SRC = (
    "'self'",
    "stats.data.gouv.fr",
    "ws:",
    "api-adresse.data.gouv.fr",
)
if DEBUG:
    CSP_CONNECT_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources of plugins
CSP_OBJECT_SRC = (
    "'self'",
    "cellar-c2.services.clever-cloud.com",
)
if DEBUG:
    CSP_OBJECT_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources of media (audio and video)
CSP_MEDIA_SRC = (
    "'self'",
    "cellar-c2.services.clever-cloud.com",
)
if DEBUG:
    CSP_MEDIA_SRC += CSP_DEBUG_DOMAINS

# CSP valid sources for loading frames
CSP_FRAME_SRC = ("'self'",)
if DEBUG:
    CSP_FRAME_SRC += CSP_DEBUG_DOMAINS

# Feature flags
ENABLE_XP_RESERVATION = os.getenv("ENABLE_XP_RESERVATION") == "True"
ENABLE_PARTNERS = os.getenv("ENABLE_PARTNERS") == "True"
