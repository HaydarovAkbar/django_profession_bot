import os

from decouple import config

from settings import BASE_DIR

DEBUG = config('DEBUG', cast=bool)
# ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
