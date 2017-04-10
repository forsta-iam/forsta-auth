from django.urls import reverse
from social_django.utils import load_backend, load_strategy


class BackendMeta(object):
    registry = {}

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


class TwitterBackendMeta(BackendMeta):
    backend_id = 'twitter'
    name = 'Twitter'
    font_icon = 'fa fa-twitter'

    @property
    def username(self):
        return self.user_social_auth.extra_data['access_token']['screen_name']

    @property
    def profile_url(self):
        return 'https://twitter.com/' + self.username


class GoogleOAuth2BackendMeta(BackendMeta):
    backend_id = 'google-oauth2'
    name = 'Google'
    font_icon = 'fa fa-google'


class ORCIDBackendMeta(BackendMeta):
    backend_id = 'orcid'
    name = 'ORCID'
    font_icon = 'ai ai-orcid'


class FacebookBackendMeta(BackendMeta):
    backend_id = 'facebook'
    name = 'Facebook'
    font_icon = 'fa fa-facebook-official'


class FigshareBackendMeta(BackendMeta):
    backend_id = 'figshare'
    name = 'Figshare'
    font_icon = 'ai ai-figshare'


class LinkedinBackendMeta(BackendMeta):
    backend_id = 'linkedin'
    name = 'LinkedIn'
    font_icon = 'fa fa-linkedin'


class GithubBackendMeta(BackendMeta):
    backend_id = 'github'
    name = 'GitHub'
    font_icon = 'fa fa-github'


class SAMLBackendMeta(BackendMeta):
    backend_id = 'saml'
    name = 'SAML'
    font_icon = 'fa fa-university'

    @property
    def name(self):
        saml_backend = load_backend(
            load_strategy(),
            "saml",
            redirect_uri=reverse('social:complete', args=("saml",))
        )
        return saml_backend.get_idp(self.user_social_auth.uid.split(':')[0]).conf['label']


    @property
    def username(self):
        return '{} at {}'.format(self.user_social_auth.uid.split(':')[1], self.name)


for backend_meta in (TwitterBackendMeta, GoogleOAuth2BackendMeta, ORCIDBackendMeta, FacebookBackendMeta,
                     FigshareBackendMeta, LinkedinBackendMeta, GithubBackendMeta, SAMLBackendMeta):
    BackendMeta.registry[backend_meta.backend_id] = backend_meta()
