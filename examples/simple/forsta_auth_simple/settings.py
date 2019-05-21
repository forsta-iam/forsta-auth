from idm_auth.settings import *  # pragma: noqa

SECRET_KEY = "very secret key"

ALLOWED_HOSTS = ['*']

DEBUG = True

INSTALLED_APPS.insert(0, 'forsta_brand')