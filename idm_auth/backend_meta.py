class BackendMeta(object):
    registry = {}

    @classmethod
    def wrap(cls, user_social_auth):
        print(user_social_auth.provider, type(cls.registry.get(user_social_auth.provider)))
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

for backend_meta in (TwitterBackendMeta, GoogleOAuth2BackendMeta, ORCIDBackendMeta):
    BackendMeta.registry[backend_meta.backend_id] = backend_meta()
