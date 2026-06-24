"""

Production settings for core project.



These settings are for production environment.

"""

import os

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:

    raise ValueError(
        "DJANGO_SECRET_KEY environment variable must be set for production"
    )


# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False


ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")


# Database - Use environment variables for production

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}


# Static files

STATIC_ROOT = BASE_DIR / "staticfiles"  # این خط را اضافه کنید


# Cache using Redis (for production)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/1"),
    }
}


# Security settings for production

SECURE_SSL_REDIRECT = False  # Disabled for local development without SSL

SESSION_COOKIE_SECURE = False  # Disabled for local development without SSL

CSRF_COOKIE_SECURE = False  # Disabled for local development without SSL

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"
