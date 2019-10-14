import logging

import requests
from django.conf import settings
from django.core.checks import Warning, register
from social_core.backends.google import GoogleOAuth2
from social_core.backends.linkedin import LinkedinOAuth2

logger = logging.getLogger(__name__)


W001 = Warning(
    "Incorrect Twitter auth credentials. Ensure that the SOCIAL_AUTH_TWITTER_* settings are correctly configured.",
    id='forsta_auth.W001',
)

W002 = Warning(
    "Incorrect Google auth credentials. Ensure that the SOCIAL_AUTH_GOOGLE_OAUTH2_* settings are correctly configured.",
    id='forsta_auth.W002',
)

W003 = Warning(
    "Incorrect LinkedIn auth credentials. Ensure that the SOCIAL_AUTH_LINKEDIN_OAUTH2_* settings are correctly "
    "configured.",
    id='forsta_auth.W003',
)


@register('integration', deploy=True)
def check_twitter_credentials(app_configs, **kwargs):
    if getattr(settings, 'SOCIAL_AUTH_TWITTER_KEY', None) is not None:
        response = requests.post('https://api.twitter.com/oauth2/token',
                                 {'grant_type': 'client_credentials'},
                                 auth=(settings.SOCIAL_AUTH_TWITTER_KEY,
                                       settings.SOCIAL_AUTH_TWITTER_SECRET))
        try:
            response.raise_for_status()
        except requests.HTTPError:
            return [W001]
    return []


@register('integration', deploy=True)
def check_google_oauth2_credentials(app_configs, **kwargs):
    if getattr(settings, 'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', None) is not None:
        auth = GoogleOAuth2()
        response = requests.post(auth.access_token_url(),
                                 {'grant_type': 'authorization_code',
                                  'code': 'invalid',
                                  'client_id': auth.setting('KEY'),
                                  'client_secret': auth.setting('SECRET')})
        if response.status_code == 401:
            return [W002]
    return []


@register('integration', deploy=True)
def check_linkedin_auth2_credentials(app_configs, **kwargs):
    if getattr(settings, 'SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY', None) is not None:
        auth = LinkedinOAuth2()
        response = requests.post(auth.access_token_url(),
                                 {'grant_type': 'client_credentials',
                                  'client_id': auth.setting('KEY'),
                                  'client_secret': auth.setting('SECRET')})
        data = response.json()
        if data.get('error') in {'invalid_client_id', 'invalid_client'}:
            return [W003]
    return []
