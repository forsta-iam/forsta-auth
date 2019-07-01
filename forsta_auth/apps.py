import os

import requests
from django.apps import apps, AppConfig
from django.conf import settings
from django.db import connection
from django.db.models.signals import post_delete, post_save
from django.utils.module_loading import import_string

from forsta_auth.tasks.social_accounts import sync_social_accounts


class IDMAuthConfig(AppConfig):
    name = 'forsta_auth'
    session = None

    def ready(self):
        self.session = requests.Session()
        try:
            from requests_negotiate import HTTPNegotiateAuth
        except ImportError:
            self.session.auth = None
        else:
            self.session.auth = HTTPNegotiateAuth(
                negotiate_client_name=getattr(settings, 'CLIENT_PRINCIPAL_NAME', None))

        # Support explicitly using system (or other) trust
        if 'SSL_CERT_FILE' in os.environ:
            self.session.verify = os.environ['SSL_CERT_FILE']

        if settings.BROKER_ENABLED:
            from social_django.models import UserSocialAuth
            user_serializer = import_string(getattr(settings, 'AUTH_USER_SERIALIZER',
                                                    'forsta_auth.serializers.UserSerializer'))

            apps.get_app_config('idm_broker').register_notifications([
                {'serializer': user_serializer, 'exchange': 'user'},
            ])

            post_delete.connect(self.user_social_auth_updated, UserSocialAuth)
            post_save.connect(self.user_social_auth_updated, UserSocialAuth)

    def user_social_auth_updated(self, instance, **kwargs):
        if not getattr(instance, '_sync_social_auth_pending', False) and instance.user:
            instance._sync_social_auth_pending = True
            connection.on_commit(lambda: sync_social_accounts.delay(instance.user.pk))
