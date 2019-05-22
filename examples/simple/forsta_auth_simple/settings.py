import environ

from forsta_auth.settings import *  # pragma: noqa

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['*']),
)

SECRET_KEY = "very secret key"

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
