import os
from datetime import timedelta

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Environment dependent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SECRET_KEY = env.str("SECRET_KEY")

if env.str("EMAIL_URL", ""):
    EMAIL_CONFIG = env.email()
    vars().update(EMAIL_CONFIG)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")

S3_ENDPOINT_URL = env.str("S3_ENDPOINT_URL")
S3_BUCKET = env.str("S3_BUCKET")
S3_ACCESS_KEY = env.str("S3_ACCESS_KEY")
S3_SECRET_KEY = env.str("S3_SECRET_KEY")

SESSION_COOKIE_DOMAIN = env.str("SESSION_COOKIE_DOMAIN")
SESSION_COOKIE_HTTPONLY = env.bool("SESSION_COOKIE_HTTPONLY")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE")

SENTRY_DSN = env.str("SENTRY_DSN", "")

DATABASES = {"default": env.db()}

DEBUG = False

AUTHENTICATION_BACKENDS = ("nickelodeon.backends.CaseInsensitiveModelBackend",)

# Application definition
INSTALLED_APPS = [
    "nickelodeon",
    "corsheaders",
    "rest_framework",
    "knox",
    "resumable",
    "raven.contrib.django.raven_compat",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "django.contrib.postgres",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "nickelodeon.urls"

STATIC_ROOT = os.path.join(BASE_DIR, "..", "static")
STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "..", "templates"),
        ],
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

WSGI_APPLICATION = "nickelodeon.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Django Rest Framework Config
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "nickelodeon.api.auth.TokenAuthSupportQueryString",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [],
}

# Django CORS Headers
CORS_ORIGIN_ALLOW_ALL = True

# Django Rest Knox
REST_KNOX = {
    "TOKEN_TTL": timedelta(days=7),
    "AUTO_REFRESH": True,
}

# Nickelodeon
NICKELODEON_MUSIC_ROOT = os.path.join(BASE_DIR, "..", "media")

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "..", "tmp")

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        traces_sample_rate=0.001,
    )

try:
    from .settings_override import *  # noqa: F403, F401
except ImportError:
    pass
