"""
Base settings for core project.

This file contains settings that are common to all environments.
"""

from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    # 1. Django Default Apps
    # --------------------
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ---
    # 2. Third-Party Apps (External)
    # ------------------------------
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    # ---
    # 3. Project Apps (Internal)
    # --------------------------
    "accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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

WSGI_APPLICATION = "core.wsgi.application"

# Password validation
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

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============== DRF Configuration ==============
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ============== JWT Configuration ==============
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=180),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

# ============== OTP Configuration ==============
AUTH_OTP_LENGTH = 5
AUTH_CACHE_TIMEOUT = 120
AUTH_PHONE_REGEX_PATTERN = r"^(09)\d{9}$"

# ============== drf-spectacular Configuration ==============
SPECTACULAR_SETTINGS = {
    "TITLE": "🚀 IoT Hub API",
    "DESCRIPTION": "IoT Hub Backend API with JWT authentication and OTP-based login.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": -1,
        "docExpansion": "none",
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
    "SECURITY": [{"BearerAuth": []}],
    "SECURITY_SCHEMES": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token authentication. Usage: Authorization: Bearer <token>",
        }
    },
    "TAGS": [
        {
            "name": "🔐 Authentication",
            "description": "Authentication endpoints (OTP, login, verify)",
        },
    ],
}

# ============== SMS.ir Configuration ==============
SMS_API_URL = os.environ.get("SMS_API_URL", "https://api.sms.ir/v1/send")
SMS_TEMPLATE_ID = os.environ.get("SMS_TEMPLATE_ID", 523562)

# ============== Celery Configuration ==============
CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", "amqp://iotuser:iotpass@localhost:5672//"
)
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 20 * 60

CELERY_BEAT_SCHEDULE = {}
