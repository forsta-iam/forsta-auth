from social_core.backends.oauth import BaseOAuth2


class ORCIDSandboxAuth(BaseOAuth2):
    """Twitter OAuth authentication backend"""
    name = 'orcid'
    #EXTRA_DATA = [('id', 'id')]
    REQUEST_TOKEN_METHOD = 'POST'
    ACCESS_TOKEN_METHOD = 'POST'
    AUTHORIZATION_URL = 'https://sandbox.orcid.org/oauth/authorize'
    REQUEST_TOKEN_URL = 'https://api.sandbox.orcid.org/oauth/token'
    ACCESS_TOKEN_URL = 'https://api.sandbox.orcid.org/oauth/token'
    REDIRECT_STATE = True
