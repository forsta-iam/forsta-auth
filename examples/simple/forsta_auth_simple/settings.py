import json

import environ

from django.conf import global_settings
from forsta_auth.settings import *  # pragma: noqa

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['*']),
    SECURE_PROXY_SSL_HEADER_NAME=(str, None),
    SECURE_PROXY_SSL_HEADER_VALUE=(str, None),

    # Branding
    ORGANIZATION_NAME=(str, TEXT_BRANDING['organization_name']),
    ORGANIZATION_NAME_IN_CONTEXT=(str, TEXT_BRANDING['organization_name_in_context']),
    YOUR_ACCOUNT=(str, TEXT_BRANDING['your_account']),
    AN_ACCOUNT=(str, TEXT_BRANDING['an_account']),
)

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

TEMPLATE_DEBUG = DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

INSTALLED_APPS = [
    'forsta_auth_simple',
    'forsta_brand',
] + INSTALLED_APPS

try:
    insert_whitenoise_at = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1
except ValueError:
    insert_whitenoise_at = 0
MIDDLEWARE.insert(insert_whitenoise_at, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DATABASES = {
    'default': env.db(),
}


DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='accounts@example.org')

# nginx ingress uses this HTTP request header to say that the original request was HTTPS.
# This is used when constructing URLs in responses.
SECURE_PROXY_SSL_HEADER = (env('SECURE_PROXY_SSL_HEADER_NAME'),
                           env('SECURE_PROXY_SSL_HEADER_VALUE'))
if not all(SECURE_PROXY_SSL_HEADER):
    SECURE_PROXY_SSL_HEADER = None


TEXT_BRANDING = {
    'organization_name': env('ORGANIZATION_NAME'),
    'organization_name_in_context': env('ORGANIZATION_NAME_IN_CONTEXT'),
    'your_account': env('YOUR_ACCOUNT'),
    'an_account': env('AN_ACCOUNT'),
}

LOGGING = env('LOGGING', cast=json.loads, default=global_settings.LOGGING)


INSTALLED_APPS.append('request_id')
MIDDLEWARE.insert(0, 'request_id.middleware.RequestIdMiddleware')