import django
import email.utils
import os
from social.pipeline import DEFAULT_AUTH_PIPELINE

DEBUG = os.environ.get('DJANGO_DEBUG')

USE_TZ = True
TIME_ZONE = 'Europe/London'


ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split() if not DEBUG else ['*']

try:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
except KeyError:
    if DEBUG:
        SECRET_KEY = 'very secret key'
    else:
        raise

if 'DJANGO_ADMINS' in os.environ:
    ADMINS = [email.utils.parseaddr(addr.strip()) for addr in os.environ['DJANGO_ADMINS'].split(',')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + (
            'postgresql' if django.VERSION >= (1, 9) else 'postgresql_psycopg2'),
        'NAME': os.environ.get('DATABASE_NAME', 'idm_auth'),
    },
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'idm_auth.apps.IDMAuthConfig',
    'idm_brand',
    'social.apps.django_app.default',
    'reversion',
    # Two-factor auth
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'otp_yubikey',
]
try:
    __import__('django_extensions')
except ImportError:
    pass
else:
    INSTALLED_APPS.append('django_extensions')

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Always include for two-factor auth
    'django_otp.middleware.OTPMiddleware',

]

AUTHENTICATION_BACKENDS = (
    'social.backends.open_id.OpenIdAuth',
    'social.backends.google.GoogleOpenId',
    'social.backends.google.GoogleOAuth2',
    'social.backends.google.GoogleOAuth',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.yahoo.YahooOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
                'django.template.context_processors.static',
            ),
        },
    },
]

AUTH_USER_MODEL = 'idm_auth.User'

ROOT_URLCONF = 'idm_auth.urls'

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/account/profile/'
LOGIN_URL = '/login/'

SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

SOCIAL_AUTH_PIPELINE = list(DEFAULT_AUTH_PIPELINE)
SOCIAL_AUTH_PIPELINE.remove('social.pipeline.user.user_details')
SOCIAL_AUTH_PIPELINE.remove('social.pipeline.user.get_username')
SOCIAL_AUTH_PIPELINE[SOCIAL_AUTH_PIPELINE.index('social.pipeline.user.create_user')] = 'idm_auth.pipeline.create_user'


# AMQP
BROKER_PARAMS = {
    'hostname': os.environ.get('AMQP_BROKER_HOSTNAME', 'localhost'),
    'userid': os.environ.get('AMQP_BROKER_USERNAME', 'guest'),
    'password': os.environ.get('AMQP_BROKER_PASSWORD', 'guest'),
    'virtual_host': os.environ.get('AMQP_BROKER_VHOST', '/'),
    'ssl': bool(os.environ.get('AMQP_BROKER_SSL')),
}
BROKER_PREFIX = 'idm.auth.'

IDM_CORE_URL = os.environ.get('IDENTITY_API_URL', 'http://localhost:8000/')