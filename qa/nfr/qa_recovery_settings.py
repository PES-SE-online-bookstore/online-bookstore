"""Isolated recovery probe only; never use as deployed settings."""
import os
from urllib.parse import urlparse
from config.settings import *  # noqa: F403

target = urlparse(os.environ["QA_RESTORE_URL"])
if target.hostname not in {"localhost", "127.0.0.1"} or target.path != "/qa_recovery_test":
    raise RuntimeError("Restore target must be loopback /qa_recovery_test")
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql", "NAME": "qa_recovery_test",
    "USER": target.username, "PASSWORD": target.password,
    "HOST": target.hostname, "PORT": target.port or 5432,
}}
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
