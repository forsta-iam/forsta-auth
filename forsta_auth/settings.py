import django
import email.utils

import kombu
import os
from django.urls import reverse
from django.utils.functional import lazy
from django.conf import global_settings

from environ import Env

env = Env()

DEBUG = env('DEBUG', cast=bool, default=False)  # Enable Django's DEBUG mode. Should not be used in production
TEMPLATE_DEBUG = env('TEMPLATE_DEBUG', cast=bool, default=DEBUG)
SECRET_KEY = env('SECRET_KEY')

USE_TZ = env('USE_TZ', cast=bool, default=True)
TIME_ZONE = env('TIME_ZONE', default='Europe/London')


ALLOWED_HOSTS = env('ALLOWED_HOSTS', cast=list, default=['*'] if DEBUG else [])

ADMINS = [email.utils.parseaddr(addr.strip())
          for addr in env('ADMINS', cast=list, default=[])]

MANAGERS = [email.utils.parseaddr(addr.strip())
            for addr in env('MANAGERS', cast=list, default=[])]

DATABASES = {
    'default': env.db(default='postgres:///forsta-auth'),
}

INSTALLED_APPS = [
    'forsta_auth',
    # 'forsta_auth.auth_core_integration.apps.IDMAuthCoreIntegrationConfig',
    'forsta_auth.onboarding',
    'forsta_auth.oidc',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'social_django',
    'reversion',
    'rest_framework',
    # Two-factor auth
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    #'otp_yubikey',
    'django_registration',
    # OpenID Connect
    'oidc_provider',
    'zxcvbn_password',
    'corsheaders',
]

try:
    __import__('idm_broker')
except ImportError:
    BROKER_ENABLED = False
else:
    INSTALLED_APPS.append('idm_broker')
    BROKER_ENABLED = True


try:
    __import__('django_extensions')
except ImportError:
    pass
else:
    INSTALLED_APPS.append('django_extensions')

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'oidc_provider.middleware.SessionManagementMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Always include for two-factor auth
    'django_otp.middleware.OTPMiddleware',
    'forsta_auth.middleware.SocialAuthExceptionMiddleware',
    'forsta_auth.onboarding.middleware.OnboardingMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.username.UsernameAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'forsta_auth.social_backend.ORCIDSandboxAuth',
    # The authentication form will forbid inactive users from logging in regardless, but this means we can present them
    # with a "not yet active" message
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'forsta_auth.oidc.authentication.BearerAuthentication',
    )
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'forsta_auth.context_processors.forsta_auth',
                'forsta_auth.context_processors.two_factor_enabled',
                'forsta_auth.context_processors.features_enabled',
                'forsta_auth.onboarding.context_processors.onboarding',
            ],
        },
    },
]

AUTH_USER_MODEL = 'forsta_auth.User'

ROOT_URLCONF = 'forsta_auth.urls'

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT')

MEDIA_ROOT = env('MEDIA_ROOT')

LOGIN_REDIRECT_URL = '/profile/'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

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
    'forsta_auth.onboarding.pipeline.confirm_user_details',

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
    'forsta_auth.pipeline.two_factor.add_user_id',
    'forsta_auth.pipeline.two_factor.perform_two_factor',

)


# For kombu, generally AMQP
BROKER_TRANSPORT = env('BROKER_TRANSPORT', default='amqp')
BROKER_HOSTNAME = env('BROKER_HOSTNAME', default='localhost')
BROKER_SSL = env('BROKER_SSL', cast=bool, default=True)
BROKER_VHOST = env('BROKER_VHOST', default='/')
BROKER_USERNAME = env('BROKER_USERNAME', default='guest')
BROKER_PASSWORD = env('BROKER_PASSWORD', default='guest')
BROKER_PREFIX = env('BROKER_PREFIX', default='idm.auth.')


CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@localhost:5672//')

OIDC_EXTRA_SCOPE_CLAIMS = 'forsta_auth.oidc.claims.IDMAuthScopeClaims'

IDM_CORE_URL = env('IDM_CORE_URL', default='http://localhost:8000/')
IDM_CORE_API_URL = env('IDM_CORE_API_URL', default='http://localhost:8000/api/')

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'locale': 'en_GB',
  'fields': 'id, name, email'
}


def _get_inactive_user_url():
    return reverse('login') + '?awaiting-activation'

SOCIAL_AUTH_INACTIVE_USER_URL = lazy(_get_inactive_user_url, str)()

SESSION_COOKIE_NAME = 'idm-auth-sessionid'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7

TWO_FACTOR_LOCAL_YUBIKEY_VALIDATION = True

# The SOCIAL_AUTH_SAML_ENABLED_IDPS setting mentioned in the docs (http://psa.matiasaguirre.net/docs/backends/saml.html)
# is replaced by forsta_auth.saml.models.IDP, and you can add more with fixtures, the admin, or the load_saml_metadata
# management command.

for key in os.environ:
    if key.startswith('SOCIAL_AUTH_'):
        locals()[key] = os.environ[key]
        if key.endswith('_SCOPE'):
            locals()[key] = locals()[key].split()

EMAIL_HOST = env('EMAIL_HOST', default=None)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=None)
EMAIL_PORT = env('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=global_settings.DEFAULT_FROM_EMAIL)
SERVER_EMAIL = env('SERVER_EMAIL', default=global_settings.SERVER_EMAIL)
SUPPORT_EMAIL = env('SUPPORT_EMAIL', default=DEFAULT_FROM_EMAIL)

IDM_APPLICATION_ID = '4ff517c5-532f-42ee-afb1-a5d3da2f61d5'


PASSWORD_HASHERS = global_settings.PASSWORD_HASHERS

DEFAULT_REALM = env('DEFAULT_REALM', default='EXAMPLE.COM')
KADMIN_PRINCIPAL_NAME = env('KADMIN_PRINCIPAL_NAME', default=None)
CLIENT_PRINCIPAL_NAME = env('CLIENT_PRINCIPAL_NAME', default=None)


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
        'tasks': ['forsta_auth.auth_core_integration.tasks.process_person_update'],
    }],
}


CLAIM_ENABLED = env('CLAIM_ENABLED', cast=bool, default=False)  # Allows externally-created accounts to be claimed by users
# Two-factor auth has external dependencies, but they're fairly tightly integrated into the login flow, so we'll just
# disable setting up 2FA, and object if anyone tries to log in when they have 2FA set up.
TWO_FACTOR_ENABLED = env('TWO_FACTOR_ENABLED', cast=bool, default=True)  # Allows users to set up TOTP for two-factor auth


# Optional features requiring extra dependencies

def _optional_feature(enabled, *import_names):
    try:
        for name in import_names:
            __import__(name)
    except ImportError:
        if enabled is True:
            raise
        return False
    else:
        return enabled is not False


KERBEROS_ENABLED = _optional_feature(env('KERBEROS_ENABLED', cast=bool, default=None),  # Enables password management in an external KDC
                                     'kadmin', 'kerberos')
SSH_KEYS_ENABLED = _optional_feature(env('SSH_KEYS_ENABLED', cast=bool, default=None),  # Lets users manage SSH keys for use elsewhere
                                     'sshpubkeys')
SAML_ENABLED = _optional_feature(env('SAML_ENABLED', cast=bool, default=None),  # Allows users to use SAML for federated login
                                 'xmlsec', 'onelogin.saml2')

if KERBEROS_ENABLED:
    INSTALLED_APPS.append('forsta_auth.kerberos')
    AUTHENTICATION_BACKENDS.insert(0, 'forsta_auth.kerberos.backends.KerberosBackend')
    PASSWORD_HASHERS.append('forsta_auth.kerberos.hashers.KerberosHasher')

if SSH_KEYS_ENABLED is not False:
    INSTALLED_APPS.append('forsta_auth.ssh_key')

if SAML_ENABLED:
    INSTALLED_APPS.append('forsta_auth.saml')
    AUTHENTICATION_BACKENDS.insert(0, 'forsta_auth.saml.social_backend.SAMLAuth')
    TEMPLATES[0]['OPTIONS']['context_processors'].append('forsta_auth.saml.context_processors.idps')

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


TEXT_BRANDING = {
    'organization_name': 'Example Organization',
    'organization_name_in_context': 'the Example Organization',
    'your_account': 'your account',
    'an_account': 'an account',
    'account': 'account',
    'accounts': 'accounts',
}


OIDC_CODE_EXPIRE = env('OIDC_CODE_EXPIRE', cast=int, default=60*10)
OIDC_IDTOKEN_EXPIRE = env('OIDC_IDTOKEN_EXPIRE', cast=int, default=60*10)
OIDC_TOKEN_EXPIRE = env('OIDC_TOKEN_EXPIRE', cast=int, default=60*60)
OIDC_SESSION_MANAGEMENT_ENABLE = env('OIDC_SESSION_MANAGEMENT_ENABLE', cast=bool, default=False)  # If enabled, the Server will support Session Management 1.0 specification.
OIDC_SKIP_CONSENT_EXPIRE = env('OIDC_SKIP_CONSENT_EXPIRE', cast=int, default=30*3)  # How many days before users have to re-consent if "re-use consent" is enabled for a client.
OIDC_GRANT_TYPE_PASSWORD_ENABLE = env('OIDC_GRANT_TYPE_PASSWORD_ENABLE', cast=bool, default=False)  # Whether to allow the Resource Owner Password Credentials Grant
OIDC_INTROSPECTION_VALIDATE_AUDIENCE_SCOPE = env('OIDC_INTROSPECTION_VALIDATE_AUDIENCE_SCOPE', cast=bool, default=True)
