import datetime
import time
import unittest.mock
import uuid

import kombu
from kombu.message import Message
from django.apps import apps
from django.db import transaction
from django.test import TransactionTestCase
from kombu.utils import json

from idm_auth.tests.utils import get_fake_identity_data, update_user_from_identity_noop
from ..models import User


@unittest.mock.patch('idm_auth.auth_core_integration.utils.update_user_from_identity', update_user_from_identity_noop)
class BrokerTestCase(TransactionTestCase):
    def test_user_published(self):
        idm_broker_config = apps.get_app_config('idm_broker')
        with idm_broker_config.broker.acquire(block=True) as conn:
            queue = kombu.Queue(exclusive=True).bind(conn)
            queue.declare()
            queue.bind_to(exchange=kombu.Exchange('idm.auth.user'), routing_key='#')
            with transaction.atomic():
                user = User.objects.create(identity_id=uuid.uuid4(),
                                           primary=True, is_active=True,
                                           date_of_birth=datetime.datetime(1970, 1, 1))
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