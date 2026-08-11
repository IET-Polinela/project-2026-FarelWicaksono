#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Saat menjalankan `python manage.py test ...`, gunakan konfigurasi
    # SQLite khusus testing secara otomatis. Perintah lain seperti runserver
    # tetap memakai settings utama/PostgreSQL.
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        os.environ["DJANGO_SETTINGS_MODULE"] = "smartcity_app.test_settings"
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_app.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
