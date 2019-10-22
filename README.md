# Forstå Authentication Service and API

[![Build Status](https://travis-ci.org/forsta-iam/forsta-auth.svg?branch=master)](https://travis-ci.org/forsta-iam/forsta-auth) [![codecov](https://codecov.io/gh/forsta-iam/forsta-auth/branch/master/graph/badge.svg)](https://codecov.io/gh/forsta-iam/forsta-auth)


## Environment variables

Name | Cast | Default | Description
---- | ---- | ------- | -----------
DEBUG | `bool` | `False` | Enable Django's DEBUG mode. Should not be used in production.  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#debug)
TEMPLATE_DEBUG | `bool` | `DEBUG` |
**SECRET_KEY** |  |  |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secret-key)
USE_TZ | `bool` | `True` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#use-tz)
TIME_ZONE |  | `'Europe/London'` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#time-zone)
ALLOWED_HOSTS | `list` | `['*'] if DEBUG else []` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts)
DATABASE_URL |  | `'postgres:///forsta-auth'` |
**STATIC_ROOT** |  |  |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#static-root)
**MEDIA_ROOT** |  |  |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#media-root)
BROKER_TRANSPORT |  | `'amqp'` |
BROKER_HOSTNAME |  | `'localhost'` |
BROKER_SSL | `bool` | `True` |
BROKER_VHOST |  | `'/'` |
BROKER_USERNAME |  | `'guest'` |
BROKER_PASSWORD |  | `'guest'` |
BROKER_PREFIX |  | `'idm.auth.'` |
CELERY_BROKER_URL |  | `'amqp://guest:guest@localhost:5672//'` |
IDM_CORE_URL |  | `'http://localhost:8000/'` |
IDM_CORE_API_URL |  | `'http://localhost:8000/api/'` |
EMAIL_HOST |  | `None` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host)
EMAIL_HOST_USER |  | `None` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-user)
EMAIL_HOST_PASSWORD |  | `None` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-password)
EMAIL_PORT | `int` | `587` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-port)
EMAIL_USE_TLS | `bool` | `True` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-use-tls)
EMAIL_BACKEND |  | `'django.core.mail.backends.console.EmailBackend'` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-backend)
DEFAULT_FROM_EMAIL |  | `global_settings.DEFAULT_FROM_EMAIL` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#default-from-email)
SERVER_EMAIL |  | `global_settings.SERVER_EMAIL` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#server-email)
SUPPORT_EMAIL |  | `DEFAULT_FROM_EMAIL` |
DEFAULT_REALM |  | `'EXAMPLE.COM'` |
KADMIN_PRINCIPAL_NAME |  | `None` |
CLIENT_PRINCIPAL_NAME |  | `None` |
CLAIM_ENABLED | `bool` | `False` | Allows externally-created accounts to be claimed by users
TWO_FACTOR_ENABLED | `bool` | `True` | Allows users to set up TOTP for two-factor auth
KERBEROS_ENABLED | `bool` | `None` | Enables password management in an external KDC
SSH_KEYS_ENABLED | `bool` | `None` | Lets users manage SSH keys for use elsewhere
SAML_ENABLED | `bool` | `None` | Allows users to use SAML for federated login
OIDC_CODE_EXPIRE | `int` | `60 * 10` |
OIDC_IDTOKEN_EXPIRE | `int` | `60 * 10` |
OIDC_TOKEN_EXPIRE | `int` | `60 * 60` |
OIDC_SESSION_MANAGEMENT_ENABLE | `bool` | `False` | If enabled, the Server will support Session Management 1.0 specification.
OIDC_SKIP_CONSENT_EXPIRE | `int` | `30 * 3` | How many days before users have to re-consent if "re-use consent" is enabled for a client.
OIDC_GRANT_TYPE_PASSWORD_ENABLE | `bool` | `False` | Whether to allow the Resource Owner Password Credentials Grant
OIDC_INTROSPECTION_VALIDATE_AUDIENCE_SCOPE | `bool` | `True` |
SECURE_HSTS_INCLUDE_SUBDOMAINS | `bool` | `False` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secure-hsts-include-subdomains)
SECURE_HSTS_PRELOAD | `bool` | `False` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secure-hsts-preload)
SECURE_HSTS_SECONDS | `int` | `0` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secure-hsts-seconds)
SECURE_CONTENT_TYPE_NOSNIFF | `bool` | `True` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secure-content-type-nosniff)
SECURE_BROWSER_XSS_FILTER | `bool` | `True` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secure-browser-xss-filter)
SECURE_SSL_REDIRECT | `bool` | `False` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#secure-ssl-redirect)
SESSION_COOKIE_NAME |  | `'sessionid'` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#session-cookie-name)
SESSION_COOKIE_SECURE | `bool` | `False` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#session-cookie-secure)
CSRF_COOKIE_SECURE | `bool` | `False` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#csrf-cookie-secure)
SILENCED_SYSTEM_CHECKS | `list` | `[]` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#silenced-system-checks)
