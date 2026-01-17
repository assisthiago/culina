from app.settings.base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = [".culina.com"]
CSRF_TRUSTED_ORIGINS = ["https://*.culina.com"]

SESSION_COOKIE_DOMAIN = ".culina.com"
CSRF_COOKIE_DOMAIN = ".culina.com"
