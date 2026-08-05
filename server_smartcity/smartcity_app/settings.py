"""
Django settings for the smartcity_app project.

Backend Django REST Framework untuk aplikasi Smart City.
Disesuaikan untuk Lab Session 13 - Deployment.
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

# Untuk server production, isi DJANGO_SECRET_KEY melalui
# environment variable dan jangan menyimpan secret asli di GitHub.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-development-only-change-this-key",
)

# Lokal:
#   DJANGO_DEBUG=True
#
# Server:
#   DJANGO_DEBUG=False
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Konfigurasi ini mengikuti kebutuhan praktikum Lab 13.
# Pada production sebenarnya, sebaiknya diisi host tertentu.
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

        # Folder templates global berada sejajar dengan manage.py.
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

# Secara default project menggunakan PostgreSQL.
#
# Untuk pengujian cepat menggunakan SQLite:
#
# PowerShell:
#   $env:USE_SQLITE="1"
#
# Linux:
#   export USE_SQLITE=1

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

            # Data database dibaca dari environment variable.
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

# Folder tujuan hasil perintah:
# python manage.py collectstatic --noinput
STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# CUSTOM USER AND AUTHENTICATION
# ============================================================

AUTH_USER_MODEL = "usermanagement_24782049.User"

LOGIN_REDIRECT_URL = "home"

LOGOUT_REDIRECT_URL = "login"


# ============================================================
# DJANGO REST FRAMEWORK AND JWT
# ============================================================

REST_FRAMEWORK = {
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
# CROSS-ORIGIN RESOURCE SHARING
# ============================================================

# Frontend GitHub Pages dan backend server kampus berada
# pada origin yang berbeda.
#
# Konfigurasi terbuka ini digunakan sesuai kebutuhan praktikum.
CORS_ALLOW_ALL_ORIGINS = True


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

# Tetap menggunakan AutoField agar konsisten dengan migration
# dari lab sebelumnya.
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"