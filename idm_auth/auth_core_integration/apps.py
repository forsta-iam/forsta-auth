import urllib.parse

from django.apps import apps, AppConfig
from django.conf import settings
from django.db.models.signals import pre_save

from . import utils


class IDMAuthCoreIntegrationConfig(AppConfig):
    name = 'idm_auth.auth_core_integration'

    def ready(self):
        from idm_auth.models import User
        pre_save.connect(self.sync_identity, User)

    def sync_identity(self, instance, **kwargs):
        from idm_auth.models import User
        assert isinstance(instance, User)

        if instance.identity_id and 'identity_id' in instance.get_dirty_fields():
            utils.update_user_from_identity(instance)
        elif instance.is_active and not instance.identity_id:
            app_config = apps.get_app_config('idm_auth')
            identity_url = urllib.parse.urljoin(settings.IDM_CORE_URL, 'person/')
            data = {
                'names': [{
                    'context': 'presentational',
                    'components': [{
                        'type': 'given',
                        'value': instance.first_name,
                    }, ' ', {
                        'type': 'family',
                        'value': instance.last_name,
                    }]
                }],
                'emails': [{
                    'context': 'home',
                    'value': instance.email,
                    'validated': True,
                }],
                'date_of_birth': instance.date_of_birth.isoformat() if instance.date_of_birth else None,
                'state': 'active',
            }
            response = app_config.session.post(identity_url, json=data)
            response.raise_for_status()
            instance.identity_id = response.json()['id']
            instance.email = ''

        elif instance.is_active and instance.identity_id and instance.primary and 'is_active' in instance.get_dirty_fields():
            utils.activate_identity(instance, instance.identity_id)
