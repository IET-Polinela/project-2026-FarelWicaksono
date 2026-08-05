"""
Django settings for the smartcity_app project.

Backend Django REST Framework untuk aplikasi Smart City.
Dikembangkan sampai Lab Session 14:
- JWT Authentication
- CORS
- Deployment
- OpenAPI Documentation
"""

import os
from pathlib import Path


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-only-change-this-key",
)

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Digunakan untuk kebutuhan praktikum dan server kampus.
ALLOWED_HOSTS = ["*"]


# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [
    # Django default applications
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party applications
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    # OpenAPI documentation - Lab 14
    "drf_spectacular",
    "django_scalar",

    # Project applications
    "usermanagement_24782049",
    "dashboard_24782049",
    "main_app",
    "about",
    "contacts",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # CorsMiddleware harus berada sebelum CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "smartcity_app.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
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


WSGI_APPLICATION = "smartcity_app.wsgi.application"


# ============================================================
# DATABASE
# ============================================================

# Untuk menggunakan SQLite sementara:
#
# PowerShell:
#   $env:USE_SQLITE="1"
#
# Untuk kembali ke PostgreSQL:
#   Remove-Item Env:USE_SQLITE

if os.getenv("USE_SQLITE") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",

            "NAME": os.getenv(
                "DB_NAME",
                "smartcity_db",
            ),

            "USER": os.getenv(
                "DB_USER",
                "postgres",
            ),

            "PASSWORD": os.getenv(
                "DB_PASSWORD",
                "",
            ),

            "HOST": os.getenv(
                "DB_HOST",
                "localhost",
            ),

            "PORT": os.getenv(
                "DB_PORT",
                "5432",
            ),
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

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


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# CUSTOM USER AND AUTHENTICATION
# ============================================================

AUTH_USER_MODEL = "usermanagement_24782049.User"

LOGIN_REDIRECT_URL = "home"

LOGOUT_REDIRECT_URL = "login"


# ============================================================
# DJANGO REST FRAMEWORK, JWT, AND OPENAPI
# ============================================================

REST_FRAMEWORK = {
    # Schema OpenAPI menggunakan drf-spectacular.
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),

    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],

    "DEFAULT_AUTHENTICATION_CLASSES": [
        (
            "rest_framework_simplejwt.authentication."
            "JWTAuthentication"
        ),
    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# ============================================================
# OPENAPI DOCUMENTATION - LAB SESSION 14
# ============================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Smart City Portal API",

    "DESCRIPTION": (
        "Dokumentasi REST API resmi untuk Portal "
        "Pelaporan Laporan Warga"
    ),

    "VERSION": "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,
}


# ============================================================
# CROSS-ORIGIN RESOURCE SHARING
# ============================================================

CORS_ALLOW_ALL_ORIGINS = True


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# ============================================================
# SERVER-SPECIFIC SETTINGS
# ============================================================

# local_settings.py tersedia pada server kampus dan tidak
# dimasukkan ke GitHub. File tersebut berisi konfigurasi
# database server, DEBUG, CORS, dan pengaturan server lainnya.

try:
    from .local_settings import *  # noqa: F401, F403
except ImportError:
    pass


# local_settings.py sebelumnya memiliki REST_FRAMEWORK sendiri.
# Baris ini memastikan AutoSchema drf-spectacular tetap aktif
# setelah local_settings.py dibaca.
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = (
    "drf_spectacular.openapi.AutoSchema"
)