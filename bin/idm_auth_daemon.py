import logging
import pprint

import kombu
import kombu.message
from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from kombu.mixins import ConsumerMixin

identity_queue = kombu.Queue('iam.idm_auth.identity', exchange=kombu.Exchange('iam.idm.identity', type='topic'), auto_declare=True, routing_key='#')


class IDMAuthDaemon(ConsumerMixin):
    def __call__(self):
        idm_auth_config = apps.get_app_config('idm_auth')
        with idm_auth_config.broker.acquire(block=True) as conn:
            self.connection = conn
            self.run()

    def get_consumers(self, Consumer, channel):
        print(Consumer, channel)
        return [Consumer(queues=[identity_queue],
                         accept=['json'],
                         callbacks=[self.process_identity],
                         auto_declare=True)]

    def process_identity(self, body, message):
        from idm_auth import models

        with transaction.atomic(savepoint=False):
            assert isinstance(message, kombu.message.Message)
            action, id = message.delivery_info['routing_key'].split('.')
            if action in ('created', 'updated'):
                try:
                    user = models.User.objects.get(id=id)
                except models.User.DoesNotExist:
                    user = models.User(id=id)
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


if __name__ == '__main__':
    import django
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

    django.setup()
    daemon = IDMAuthDaemon()
    daemon()