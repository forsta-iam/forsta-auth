from django.conf import settings
from django.contrib.auth import get_backends
from django.utils.functional import cached_property
from social_core.backends.base import BaseAuth


class BackendMetaMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        if cls.backend_id:
            cls.registry[cls.backend_id] = cls()
        return cls


class BackendMeta(metaclass=BackendMetaMetaclass):
    registry = {}
    backend_id = None

    @classmethod
    def wrap(cls, user_social_auth):
        return type(cls.registry.get(user_social_auth.provider))(user_social_auth)

    def __init__(self, user_social_auth=None):
        self.user_social_auth = user_social_auth

    @property
    def username(self):
        return self.user_social_auth.uid

    @property
    def provider(self):
        return self.user_social_auth.provider

    @property
    def id(self):
        return self.user_social_auth.id

    @cached_property
    def enabled(self):
        return any(isinstance(b, BaseAuth) and b.name == self.backend_id and all(b.get_key_and_secret())
                   for b in get_backends())

    @property
    def show(self):
        return self.enabled


class TwitterBackendMeta(BackendMeta):
    backend_id = 'twitter'
    name = 'Twitter'
    font_icon = 'fab fa-twitter'

    @property
    def username(self):
        return self.user_social_auth.extra_data['access_token']['screen_name']

    @property
    def profile_url(self):
        return 'https://twitter.com/' + self.username


class GoogleOAuth2BackendMeta(BackendMeta):
    backend_id = 'google-oauth2'
    name = 'Google'
    font_icon = 'fab fa-google'


class ORCIDBackendMeta(BackendMeta):
    backend_id = 'orcid'
    name = 'ORCID'
    font_icon = 'ai ai-orcid'


class FacebookBackendMeta(BackendMeta):
    backend_id = 'facebook'
    name = 'Facebook'
    font_icon = 'fab fa-facebook'


class FigshareBackendMeta(BackendMeta):
    backend_id = 'figshare'
    name = 'Figshare'
    font_icon = 'ai ai-figshare'


class LinkedinBackendMeta(BackendMeta):
    backend_id = 'linkedin-oauth2'
    name = 'LinkedIn'
    font_icon = 'fab fa-linkedin'


class GithubBackendMeta(BackendMeta):
    backend_id = 'github'
    name = 'GitHub'
    font_icon = 'fab fa-github'

    @property
    def username(self):
        return self.user_social_auth.extra_data['login']

    @property
    def profile_url(self):
        return 'https://github.com/' + self.username
