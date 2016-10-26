import requests
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from kombu import connections
from kombu.connection import Connection


class IDMAuthConfig(AppConfig):
    name = 'idm_auth'

    def ready(self):
        self.session = requests.Session()

        self.broker = connections[Connection(**settings.BROKER_PARAMS)]
        self.broker_prefix = settings.BROKER_PREFIX

        from . import broker
        broker.init(self.broker)
        post_save.connect(broker.model_changed)
        post_delete.connect(broker.model_deleted)