"""
A django-rest-framework authentication backend for requests made with OIDC Bearer tokens


"""
import logging
import operator

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from oidc_provider.lib.errors import BearerTokenError
from rest_framework import authentication, exceptions
from rest_framework.request import Request

from oidc_provider.lib.utils.oauth2 import extract_access_token
from oidc_provider.models import Token

logger = logging.getLogger(__name__)

SCOPE_PERMISSION_MAP = getattr(settings, 'SCOPE_PERMISSION_MAP', {})


class UserProxy:
    def __init__(self, user: AbstractUser, scopes):
        perms = set()
        perms.update(*(SCOPE_PERMISSION_MAP.get(scope, ()) for scope in scopes))
        self._user, self._perms = user, perms

    def has_perm(self, perm, obj=None):
        if perm in self._perms:
            return self._user.has_perm(perm, obj)

    def __getattribute__(self, name):
        print("USER ATTR", name)
        if name in ('has_perm', '_user', '_perms'):
            return super().__getattribute__(name)
        else:
            return getattr(self._user, name)

    def __setattr__(self, name, value):
        if name in ('_user', '_perms'):
            super().__setattr__(name, value)
        else:
            setattr(self._user, name, value)


class BearerAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request: Request):
        access_token = extract_access_token(request)
        if not access_token:
            return None

        try:
            try:
                token = Token.objects.get(access_token=access_token)
            except Token.DoesNotExist:
                logger.debug('[UserInfo] Token does not exist: %s', access_token)
                raise BearerTokenError('invalid_token')

            if token.has_expired():
                logger.debug('[UserInfo] Token has expired: %s', access_token)
                raise BearerTokenError('invalid_token')
        except BearerTokenError as error:
            exc = exceptions.AuthenticationFailed()
            exc.auth_header = 'Bearer error="{0}", error_description="{1}"'.format(
                error.code, error.description)
            raise exc from error

        return UserProxy(token.user, token.scope), token
