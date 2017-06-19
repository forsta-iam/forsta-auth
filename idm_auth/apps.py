import requests
from requests_negotiate import HTTPNegotiateAuth
from django.apps import apps, AppConfig
from django.conf import settings
from django.db import connection
from django.db.models.signals import post_delete, post_save
from requests.auth import HTTPBasicAuth

from idm_auth.tasks.social_accounts import sync_social_accounts


class IDMAuthConfig(AppConfig):
    name = 'idm_auth'

    def ready(self):
        self.session = requests.Session()
        self.session.auth = HTTPNegotiateAuth(negotiate_client_name=getattr(settings, 'CLIENT_PRINCIPAL_NAME', None))

        from social_django.models import UserSocialAuth
        from . import models, serializers

        apps.get_app_config('idm_broker').register_notifications([
            {'serializer': serializers.UserSerializer, 'exchange': 'user'},
        ])

        post_delete.connect(self.user_social_auth_updated, UserSocialAuth)
        post_save.connect(self.user_social_auth_updated, UserSocialAuth)

    def user_social_auth_updated(self, instance, **kwargs):
        if not getattr(instance, '_sync_social_auth_pending', False):
            instance._sync_social_auth_pending = True
            connection.on_commit(lambda: sync_social_accounts.delay(instance.user.pk))