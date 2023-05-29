import os
from settings import BASE_DIR

from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

TOKEN = config('TOKEN')
