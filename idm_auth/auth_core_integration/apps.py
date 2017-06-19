import urllib.parse

from django.apps import apps, AppConfig
from django.conf import settings
from django.db.models.signals import pre_save,pre_delete


class IDMAuthCoreIntegrationConfig(AppConfig):
    name = 'idm_auth.auth_core_integration'

    def ready(self):
        from idm_auth.models import User
        from social_django.models import UserSocialAuth
        pre_save.connect(self.create_identity, User)
        pre_save.connect(self.update_social_auth, UserSocialAuth)
        pre_delete.connect(self.delete_social_auth, UserSocialAuth)

    def create_identity(self, instance, **kwargs):
        from idm_auth.models import User
        assert isinstance(instance, User)
        if instance.is_active and not instance.identity_id:
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

    def update_social_auth(self, instance, **kwargs):
        pass

    def delete_social_auth(self, instance, **kwargs):
        from idm_auth.backend_meta import BackendMeta
        from idm_auth.models import User
        identity = instance.user
        assert isinstance(identity, User)
        usa = BackendMeta.wrap(instance)