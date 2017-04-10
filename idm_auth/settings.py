import django
import email.utils
import os
from social_core.pipeline import DEFAULT_AUTH_PIPELINE

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
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'idm_auth.apps.IDMAuthConfig',
    'idm_auth.onboarding',
    'idm_auth.saml',
    'idm_brand',
    'idm_broker.apps.IDMBrokerConfig',
    'social_django',
    'reversion',
    'rest_framework',
    # Two-factor auth
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'otp_yubikey',
    # OpenID Connect
    'oidc_provider',
    # Kerberos auth
    'django_auth_kerberos',
]
try:
    __import__('django_extensions')
except ImportError:
    pass
else:
    INSTALLED_APPS.append('django_extensions')

SITE_ID = 1

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
    'django_auth_kerberos.backends.KrbBackend',
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.username.UsernameAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId',
    'idm_auth.saml.social_backend.SAMLAuth',
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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.static',
                'idm_auth.context_processors.two_factor_enabled',
            ),
        },
    },
]

AUTH_USER_MODEL = 'idm_auth.User'

ROOT_URLCONF = 'idm_auth.urls'

STATIC_URL = '/static/'

LOGIN_REDIRECT_URL = '/account/profile/'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    'idm_auth.pipeline.creation.confirm_user_details',

    # Send a validation email to the user to verify its email address.
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address.
    # 'social.pipeline.social_auth.associate_by_email',

    # Create an identity and user account if we haven't found one yet.
    'idm_auth.pipeline.creation.create_user',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # If the user has two-factor authentication enabled, let's do that.
    'idm_auth.pipeline.two_factor.add_user_id',
    'idm_auth.pipeline.two_factor.perform_two_factor',

)


# For kombu, generally AMQP
BROKER_ENABLED = bool(os.environ.get('BROKER_ENABLED'))
BROKER_TRANSPORT = os.environ.get('BROKER_TRANSPORT', 'amqp')
BROKER_HOSTNAME= os.environ.get('BROKER_HOSTNAME', 'localhost')
BROKER_SSL = os.environ.get('BROKER_SSL', 'yes').lower() not in ('no', '0', 'off', 'false')
BROKER_VHOST= os.environ.get('BROKER_VHOST', '/')
BROKER_USERNAME = os.environ.get('BROKER_USERNAME', 'guest')
BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD', 'guest')
BROKER_PREFIX = os.environ.get('BROKER_PREFIX', 'idm.auth.')

OIDC_USERINFO = 'idm_auth.oidc.get_userinfo'


IDM_CORE_URL = os.environ.get('IDENTITY_API_URL', 'http://localhost:8000/')

SOCIAL_AUTH_SAML_ORG_INFO = {
    "en-GB": {
        "name": "penguin-colony",
        "displayname": "Penguin Colony at the University of Oxford",
        "url": "https://penguin-colony.oucs.ox.ac.uk/",
    }
}

SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = SOCIAL_AUTH_SAML_SUPPORT_CONTACT = {
    "givenName": "Alexander Dutton",
    "emailAddress": "alexander.dutton@it.ox.ac.uk",
}

SESSION_COOKIE_NAME = 'idm-auth-sessionid'

# The SOCIAL_AUTH_SAML_ENABLED_IDPS setting mentioned in the docs (http://psa.matiasaguirre.net/docs/backends/saml.html)
# is replaced by idm_auth.saml.models.IDP, and you can add more with fixtures, the admin, or the load_saml_metadata
# management command.

for key in os.environ:
    if key.startswith('SOCIAL_AUTH_'):
        locals()[key] = os.environ[key]
