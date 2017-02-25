import uuid

import kombu
from django.apps import apps
from django.db import transaction
from kombu.mixins import ConsumerMixin

user_queue = kombu.Queue('idm.auth.person',
                         exchange=kombu.Exchange('idm.core.identity', type='topic'),
                         auto_declare=True, routing_key='#')


class IDMAuthDaemon(ConsumerMixin):
    def __call__(self):
        idm_broker_config = apps.get_app_config('idm_broker')
        with idm_broker_config.broker.acquire(block=True) as conn:
            self.connection = conn
            self.run()

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[user_queue],
                         accept=['json'],
                         callbacks=[self.process_identity],
                         auto_declare=True)]

    def process_identity(self, body, message):
        from idm_auth import models

        with transaction.atomic(savepoint=False):
            assert isinstance(message, kombu.message.Message)
            _, action, id = message.delivery_info['routing_key'].split('.')
            id = uuid.UUID(id)
            if action in ('created', 'updated'):
                try:
                    user = models.User.objects.get(identity_id=id, primary=True)
                except models.User.DoesNotExist:
                    if body['state'] == ('new', 'ready_for_claim'):
                        # No need to create users here before they've been claimed.
                        return
                    user = models.User(identity_id=id, primary=True)
                user.state = body['state']
                #user.email = body['primary_email'] or body['rescue_email']
                user.save()
                message.ack()
            elif action == 'deleted':
                for user in models.Identity.objects.filter(id=id):
                    user.delete()
                message.ack()
            else:
                message.reject()
