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
**CELERY_BROKER_URL** |  |  |
IDM_CORE_URL |  | `'http://localhost:8000/'` |
IDM_CORE_API_URL |  | `'http://localhost:8000/api/'` |
EMAIL_HOST |  | `None` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host)
EMAIL_HOST_USER |  | `None` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-user)
EMAIL_HOST_PASSWORD |  | `None` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-host-password)
EMAIL_PORT | `int` | `587` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-port)
EMAIL_USE_TLS | `bool` | `True` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-use-tls)
EMAIL_BACKEND |  | `'django.core.mail.backends.console.EmailBackend'` |  [See Django documentation](https://docs.djangoproject.com/en/2.2/ref/settings/#email-backend)
DEFAULT_REALM |  | `'EXAMPLE.COM'` |
KADMIN_PRINCIPAL_NAME |  | `None` |
CLIENT_PRINCIPAL_NAME |  | `None` |
CLAIM_ENABLED | `bool` | `False` | Allows externally-created accounts to be claimed by users
TWO_FACTOR_ENABLED | `bool` | `True` | Allows users to set up TOTP for two-factor auth
KERBEROS_ENABLED | `bool` | `None` | Enables password management in an external KDC
SSH_KEYS_ENABLED | `bool` | `None` | Lets users manage SSH keys for use elsewhere
SAML_ENABLED | `bool` | `None` | Allows users to use SAML for federated login
