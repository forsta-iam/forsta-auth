# Forstå Authentication Service and API

[![Build Status](https://travis-ci.org/forsta-iam/forsta-auth.svg?branch=master)](https://travis-ci.org/forsta-iam/forsta-auth) [![codecov](https://codecov.io/gh/forsta-iam/forsta-auth/branch/master/graph/badge.svg)](https://codecov.io/gh/forsta-iam/forsta-auth)


## Environment variables

Name | Cast | Default | Description
---- | ---- | ------- | -----------
DEBUG | `bool` | `False` |
TEMPLATE_DEBUG | `bool` | `DEBUG` |
**SECRET_KEY** |  |  |
USE_TZ | `bool` | `True` |
TIME_ZONE |  | `'Europe/London'` |
ALLOWED_HOSTS | `list` | `['*'] if DEBUG else []` |
DATABASE_URL |  | `'postgres:///forsta-auth'` |
**STATIC_ROOT** |  |  |
**MEDIA_ROOT** |  |  |
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
EMAIL_HOST |  | `None` |
EMAIL_HOST_USER |  | `None` |
EMAIL_HOST_PASSWORD |  | `None` |
EMAIL_PORT | `int` | `587` |
EMAIL_USE_TLS | `bool` | `True` |
EMAIL_BACKEND |  | `'django.core.mail.backends.console.EmailBackend'` |
DEFAULT_REALM |  | `'EXAMPLE.COM'` |
KADMIN_PRINCIPAL_NAME |  | `None` |
CLIENT_PRINCIPAL_NAME |  | `None` |
KERBEROS_ENABLED | `bool` | `None` |
SSH_KEYS_ENABLED | `bool` | `None` |
SAML_ENABLED | `bool` | `None` |
