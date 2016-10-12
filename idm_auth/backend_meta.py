class BackendMeta(object):
    registry = {}

    def __new__(cls, user_social_auth):
        subcls = cls.registry.get(user_social_auth.provider, cls)
        print(cls, subcls, user_social_auth)
        return super(cls, subcls).__new__(subcls)

    def __init__(self, user_social_auth):
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
    name = 'Twitter'
    font_awesome = 'twitter'

    @property
    def username(self):
        return self.user_social_auth.extra_data['access_token']['screen_name']

    @property
    def profile_url(self):
        return 'https://twitter.com/' + self.username


class GoogleOAuth2BackendMeta(BackendMeta):
    name = 'Google'
    font_awesome = 'google'


BackendMeta.registry.update({
    'twitter': TwitterBackendMeta,
    'google-oauth2': GoogleOAuth2BackendMeta,
})
