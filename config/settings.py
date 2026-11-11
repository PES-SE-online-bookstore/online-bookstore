"""
Django settings for config project.
"""

import os
from pathlib import Path

from csp.constants import NONE, NONCE, SELF
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local development.
# Render supplies environment variables through its dashboard.
load_dotenv(BASE_DIR / ".env")


# Security
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY is missing. Configure it in your environment "
        "or local .env file."
    )

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")

_allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    host.strip()
    for host in _allowed_hosts.split(",")
    if host.strip()
]

# Render automatically provides the actual public hostname.
_render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if _render_hostname and _render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_hostname)

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "books",
    "cart",
    "orders.apps.OrdersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "csp.middleware.CSPMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Enforcement is selected by DJANGO_CSP_ENFORCE. Keep the production Blueprint
# value aligned with Render so a Blueprint sync cannot revert enforcement.
_csp_policy = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "base-uri": [SELF],
        "object-src": [NONE],
        "frame-ancestors": [NONE],
        "form-action": [SELF],
        "script-src": [SELF, NONCE],
        "script-src-attr": [NONE],
        "style-src": [SELF, NONCE],
        "style-src-attr": [NONE],
        # Book cover URLs are seller-supplied HTTPS URLs; allow secure external
        # image hosts while preventing insecure HTTP images.
        "img-src": [SELF, "https:"],
        "font-src": [SELF],
        "connect-src": [SELF],
    }
}

if os.getenv("DJANGO_CSP_ENFORCE", "False").lower() in (
    "true",
    "1",
    "yes",
):
    CONTENT_SECURITY_POLICY = _csp_policy
else:
    CONTENT_SECURITY_POLICY_REPORT_ONLY = _csp_policy

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
}

# Require encrypted PostgreSQL connections in production. Local development and
# CI may use a local PostgreSQL server without TLS, so retain its driver default.
if not DEBUG:
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# Catalogue query-result cache (OBP-48). In-process; caches database results
# only, never rendered pages. 0 disables it. Default: 30 s in production,
# off under DEBUG (local development and the test suite, whose cache tests
# enable it explicitly).
CATALOGUE_CACHE_SECONDS = int(
    os.getenv("CATALOGUE_CACHE_SECONDS", "0" if DEBUG else "30")
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "bookstore-default",
    },
    "catalogue": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "bookstore-catalogue",
        "OPTIONS": {"MAX_ENTRIES": 500},
    },
}

# Only the catalogue diagnostics logger is configured; other loggers keep
# Python's default behaviour.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "books.catalogue": {
            "handlers": ["console"],
            "level": os.getenv(
                "CATALOGUE_LOG_LEVEL", "WARNING" if DEBUG else "INFO"
            ),
            "propagate": False,
        },
    },
}


# BOOK-F-004: password reset links expire after 30 minutes.
PASSWORD_RESET_TIMEOUT = 30 * 60


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email
EMAIL_BACKEND = os.getenv(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
GMAIL_API_CLIENT_ID = os.getenv("GMAIL_API_CLIENT_ID", "")
GMAIL_API_CLIENT_SECRET = os.getenv("GMAIL_API_CLIENT_SECRET", "")
GMAIL_API_REFRESH_TOKEN = os.getenv("GMAIL_API_REFRESH_TOKEN", "")
EMAIL_API_TIMEOUT = int(os.getenv("EMAIL_API_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "noreply@onlinebookstore.local",
)


# CSRF trusted origins
_csrf_trusted_origins = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _csrf_trusted_origins.split(",")
    if origin.strip()
]


# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = (
        os.getenv("DJANGO_SECURE_SSL_REDIRECT", "True").lower()
        in ("true", "1", "yes")
    )

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # Render terminates HTTPS before forwarding requests to Django.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Enable HSTS only after the production HTTPS deployment is verified.
    SECURE_HSTS_SECONDS = int(
        os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0")
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
