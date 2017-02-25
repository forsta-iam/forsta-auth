import requests
from django.apps import apps, AppConfig


class IDMAuthConfig(AppConfig):
    name = 'idm_auth'

    def ready(self):
        self.session = requests.Session()

        from . import models, serializers
        apps.get_app_config('idm_broker').register_notifications([
            {'serializer': serializers.UserSerializer, 'exchange': 'user'},
        ])
