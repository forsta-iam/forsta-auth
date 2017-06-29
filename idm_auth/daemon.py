import logging
import uuid

import kombu
from django.apps import apps
from django.db import transaction, connection
from kombu.mixins import ConsumerMixin, logger

from idm_auth.auth_core_integration.utils import update_user_from_identity
from idm_auth.onboarding.models import PendingActivation

logger = logging.getLogger(__name__)

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
        logger.debug("%s, %s", body, message)
        from idm_auth import models

        with transaction.atomic(savepoint=False):
            assert isinstance(message, kombu.message.Message)
            _, action, identity_id = message.delivery_info['routing_key'].split('.')
            try:
                identity_id = uuid.UUID(identity_id)
            except ValueError:
                logger.exception("Bad identity_id in routing key %s", message.delivery_info['routing_key'])
                message.reject()
                return
            if action == 'created' and body['state'] != 'established':
                message.ack()
                return
            if action in ('created', 'changed'):
                users = models.User.objects.filter(identity_id=identity_id)
                if not users.exists() and body['@type'] == 'Person' and body['state'] == 'established':
                    PendingActivation.objects.get_or_create(identity_id=identity_id)
                    logger.info("New Person identity; starting activation process")

                for user in users:
                    update_user_from_identity(user, body)
                    user.save()

                message.ack()
                logger.info("Identity changed")
            elif action == 'deleted':
                for user in models.User.objects.filter(identity_id=identity_id):
                    user.delete()
                message.ack()
            else:
                logger.warning("Unexpected action {} for identity {}".format(action, identity_id))
                message.reject()
