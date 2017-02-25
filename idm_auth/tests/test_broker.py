import uuid

import kombu
from kombu.message import Message
from django.apps import apps
from django.db import transaction
from django.test import TransactionTestCase
from kombu.utils import json

from ..models import User


class BrokerTestCase(TransactionTestCase):
    def test_user_published(self):
        idm_broker_config = apps.get_app_config('idm_broker')
        with idm_broker_config.broker.acquire(block=True) as conn:
            queue = kombu.Queue(exclusive=True).bind(conn)
            queue.declare()
            queue.bind_to(exchange=kombu.Exchange('idm.auth.user'), routing_key='#')
            with transaction.atomic():
                user = User.objects.create(identity_id=uuid.uuid4(),
                                           primary=True)
            message = queue.get()
            self.assertIsInstance(message, Message)
            self.assertEqual(message.delivery_info['routing_key'],
                             'User.created.{}'.format(str(user.id)))
            self.assertEqual(message.content_type, 'application/json')
            self.assertEqual(json.loads(message.body.decode())['@type'], 'User')