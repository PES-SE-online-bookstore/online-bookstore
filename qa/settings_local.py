"""Optional SQLite diagnostics only. CI keeps original PostgreSQL settings."""
import os

os.environ.setdefault("DJANGO_SECRET_KEY", "local-qa-diagnostics-only-not-for-deployment")
from config.settings import *  # noqa: F403,E402

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
