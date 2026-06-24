"""
Development settings for core project.

These settings are for local development only.
"""

from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-#6a1i+g3&t2g)rxc-w3)bfbo1)9l#)km2(o6dh-)ttz6wqbovb"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "web"]

# Database - SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Cache Configuration (DatabaseCache for both local and Docker) ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "my_cache_table",
    }
}

# ============== SMS.ir Configuration (hardcoded for development) ==============
SMS_API_KEY = "CIZ4Pz12Vah0kDI9cuGziFasScyDsohFzBdfYq0bcWcEM0t1"
SMS_API_URL = "https://api.sms.ir/v1/send"
SMS_TEMPLATE_ID = 523562
