# local dev settings - this is what manage.py uses by default
import os
from .base import *  # noqa

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-only-insecure-key-do-not-use-in-prod')

DEBUG = True

ALLOWED_HOSTS = ['*']
