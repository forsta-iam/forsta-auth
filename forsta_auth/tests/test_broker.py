import datetime
import time
import unittest.mock
import uuid

import kombu
from django.conf import settings
from kombu.message import Message
from django.apps import apps
from django.db import transaction
from django.test import TransactionTestCase
from kombu.utils import json

from forsta_auth.tests.utils import get_fake_identity_data, update_user_from_identity_noop
from ..models import User


@unittest.mock.patch('forsta_auth.auth_core_integration.utils.update_user_from_identity', update_user_from_identity_noop)
class BrokerTestCase(TransactionTestCase):
    @unittest.skipUnless('forsta_broker' in settings.INSTALLED_APPS,
                         "Broker support not tested if not in INSTALLED_APPS")
    def test_user_published(self):
        idm_broker_config = apps.get_app_config('forsta_broker')
        with idm_broker_config.broker.acquire(block=True) as conn:
            queue = kombu.Queue(exclusive=True).bind(conn)
            queue.declare()
            queue.bind_to(exchange=kombu.Exchange('idm.auth.user'), routing_key='#')
            connection = transaction.get_connection()
            self.assertFalse(connection.in_atomic_block)
            with transaction.atomic():
                user = User.objects.create(identity_id=uuid.uuid4(),
                                           primary=True, is_active=True)
            for i in range(5):
                message = queue.get()
                if message:
                    break
                time.sleep(0.1)
            self.assertIsInstance(message, Message)
            self.assertEqual(message.delivery_info['routing_key'],
                             'User.created.{}'.format(str(user.id)))
            self.assertEqual(message.content_type, 'application/json')
            self.assertEqual(json.loads(message.body.decode())['@type'], 'User')
