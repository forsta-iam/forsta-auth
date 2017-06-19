import http.client
from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.utils.functional import cached_property
from oidc_provider.lib.claims import ScopeClaims


class IDMAuthScopeClaims(ScopeClaims):
    @cached_property
    def profile(self):
        if self.user.identity_id:
            session = apps.get_app_config('idm_auth').session
            response = session.get(urljoin(settings.IDM_CORE_URL,
                                           'person/{}/'.format(self.user.identity_id)))
            if response.status_code == http.client.OK:
                return response.json()
            else:
                return {}
        else:
            return {}

    def scope_name(self):
        if not self.profile:
            return {}
        return {
            'name': self.profile['primary_name']['plain'],
            'given_name': self.profile['primary_name']['given'],
            'family_name': self.profile['primary_name']['family'],
            'first_name': self.profile['primary_name']['first'],
            'last_name': self.profile['primary_name']['last'],
        }

    info_name = ('Name', 'Your preferred name')

    def scope_identity(self):
        return {
            'identity_id': self.user.identity_id,
            'primary_identity': self.user.primary,
        }

    info_name = ('Identity', 'Your unique identifier in the IdM')

    def scope_email(self):
        emails = self.profile.get('emails', [])
        validated_emails = [e for e in emails if e['validated']]
        emails = validated_emails or emails
        if emails:
            return {
                'email': emails[0]['value'],
                'email_validated': emails[0]['validated'],
            }
        else:
            return {}

    info_email = ('Email', 'Your primary email address')
