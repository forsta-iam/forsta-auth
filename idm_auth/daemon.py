import uuid

import kombu
from django.apps import apps
from django.db import transaction, connection
from kombu.mixins import ConsumerMixin, logger

user_queue = kombu.Queue('idm.auth.person',
                         exchange=kombu.Exchange('idm.core.person', type='topic'),
                         auto_declare=True, routing_key='#')


class IDMAuthDaemon(ConsumerMixin):
    def __call__(self):
        idm_broker_config = apps.get_app_config('idm_broker')
        with idm_broker_config.broker.acquire(block=True) as conn:
            self.connection = conn
            self.run()

    def run(self, _tokens=1, **kwargs):
        try:
            super().run(_tokens=_tokens, **kwargs)
        finally:
            connection.close()

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
            if action == 'created' and body['state'] != 'established':
                message.ack()
                return
            if action in ('created', 'changed'):
                try:
                    user = models.User.objects.get(identity_id=id, primary=True)
                except models.User.DoesNotExist:
                    if body['state'] not in ('established', 'active'):
                        # No need to create users here before they've been claimed.
                        message.ack()
                        return
                    user = models.User(identity_id=id, primary=True, is_active=False)
                user.state = body['state']
                if body.get('primary_name'):
                    user.first_name = body['primary_name']['first']
                    user.last_name = body['primary_name']['last']
                else:
                    user.first_name = ''
                    user.last_name = ''
                user.email = body['primary_email']
                user.save()
                message.ack()
                logger.info("Identity changed")
            elif action == 'deleted':
                for user in models.Identity.objects.filter(id=id):
                    user.delete()
                message.ack()
            else:
                message.reject()
