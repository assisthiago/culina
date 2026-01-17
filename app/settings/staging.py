from app.settings.base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = [".staging.culina.com"]
CSRF_TRUSTED_ORIGINS = ["https://*.staging.culina.com"]

SESSION_COOKIE_DOMAIN = ".staging.culina.com"
CSRF_COOKIE_DOMAIN = ".staging.culina.com"
