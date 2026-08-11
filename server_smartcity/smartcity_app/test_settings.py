# Mengambil seluruh konfigurasi utama project.
from .settings import *

# Database khusus automated testing.
# SQLite dipakai agar test tidak bergantung pada PostgreSQL lokal
# dan tidak menyentuh database aplikasi utama.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Mempercepat pembuatan user selama automated testing.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]