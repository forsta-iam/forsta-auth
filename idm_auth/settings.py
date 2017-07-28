import django
import email.utils

import kombu
import os
import six
from django.urls import reverse
from django.utils.functional import lazy

DEBUG = os.environ.get('DJANGO_DEBUG')

USE_TZ = True
TIME_ZONE = 'Europe/London'


ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split() if not DEBUG else ['*']

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY and DEBUG:
    SECRET_KEY = 'very secret key'

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
    'idm_auth.apps.IDMAuthConfig',
    'idm_auth.auth_core_integration.apps.IDMAuthCoreIntegrationConfig',
    'idm_auth.kerberos.apps.KerberosConfig',
    'idm_auth.onboarding.apps.OnboardingConfig',
    'idm_auth.saml',
    'idm_brand',
    'idm_broker.apps.IDMBrokerConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'social_django',
    'reversion',
    'rest_framework',
    # Two-factor auth
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'otp_yubikey',
    'registration',
    # OpenID Connect
    'oidc_provider',
    # Kerberos auth
    'django_auth_kerberos',
    'zxcvbn_password',
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
    'idm_auth.onboarding.middleware.OnboardingMiddleware',

]

AUTHENTICATION_BACKENDS = (
    'idm_auth.kerberos.backends.KerberosBackend',
    'idm_auth.tests.social_backends.DummyBackend',
    #'django_auth_kerberos.backends.KrbBackend',
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.username.UsernameAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'idm_auth.saml.social_backend.SAMLAuth',
    # The authentication form will forbid inactive users from logging in regardless, but this means we can present them
    # with a "not yet active" message
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
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
                'idm_auth.context_processors.idm_auth',
                'idm_auth.context_processors.two_factor_enabled',
                'idm_auth.onboarding.context_processors.onboarding',
            ),
        },
    },
]

AUTH_USER_MODEL = 'idm_auth.User'

ROOT_URLCONF = 'idm_auth.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT')

LOGIN_REDIRECT_URL = '/account/profile/'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Send the user through the creation flow if we've not seen them before
    'idm_auth.onboarding.pipeline.confirm_user_details',

    # Send a validation email to the user to verify its email address.
    # This is removed as the signup flow sends the verification email
    # 'social.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address.
    # 'social.pipeline.social_auth.associate_by_email',

    # Create the record that associated the social account with this user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

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


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')

OIDC_EXTRA_SCOPE_CLAIMS = 'idm_auth.oidc.claims.IDMAuthScopeClaims'

IDM_CORE_URL = os.environ.get('IDM_CORE_URL', 'http://localhost:8000/')
IDM_CORE_API_URL = os.environ.get('IDM_CORE_API_URL', 'http://localhost:8000/api/')

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

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'locale': 'en_GB',
  'fields': 'id, name, email'
}

def _get_inactive_user_url():
    return reverse('login') + '?awaiting-activation'
SOCIAL_AUTH_INACTIVE_USER_URL = lazy(_get_inactive_user_url, six.text_type)()

SESSION_COOKIE_NAME = 'idm-auth-sessionid'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7

TWO_FACTOR_LOCAL_YUBIKEY_VALIDATION = True

# The SOCIAL_AUTH_SAML_ENABLED_IDPS setting mentioned in the docs (http://psa.matiasaguirre.net/docs/backends/saml.html)
# is replaced by idm_auth.saml.models.IDP, and you can add more with fixtures, the admin, or the load_saml_metadata
# management command.

for key in os.environ:
    if key.startswith('SOCIAL_AUTH_'):
        locals()[key] = os.environ[key]

EMAIL_HOST = os.environ.get('SMTP_SERVER')
EMAIL_HOST_USER = os.environ.get('SMTP_USER')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_USE_TLS = True

EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

IDM_APPLICATION_ID = '4ff517c5-532f-42ee-afb1-a5d3da2f61d5'

from django.conf import global_settings

PASSWORD_HASHERS = global_settings.PASSWORD_HASHERS + ['idm_auth.kerberos.hashers.KerberosHasher']

DEFAULT_REALM = os.environ.get('DEFAULT_REALM', 'EXAMPLE.COM')
KADMIN_PRINCIPAL_NAME = os.environ.get('KADMIN_PRINCIPAL_NAME')
CLIENT_PRINCIPAL_NAME = os.environ.get('CLIENT_PRINCIPAL_NAME')


AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {
        'min_length': 10,
    }
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}, {
    'NAME': 'zxcvbn_password.ZXCVBNValidator',
    'OPTIONS': {
        'min_score': 3,
        'user_attributes': ('username', 'email', 'first_name', 'last_name')
    }
}]


ONBOARDING = {
    'REGISTRATION_OPEN': True,
    'REGISTRATION_OPEN_SOCIAL': True,
    'REGISTRATION_OPEN_SAML': True,
}


IDM_BROKER = {
    'CONSUMERS': [{
        'queues': [kombu.Queue('idm.auth.person',
                               exchange=kombu.Exchange('idm.core.person', type='topic', passive=True),
                               routing_key='#')],
        'tasks': ['idm_auth.auth_core_integration.tasks.process_person_update'],
    }],
}
