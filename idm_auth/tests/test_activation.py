import json
import uuid

import kombu
import time
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from kombu import Connection
from kombu.message import Message
from kombu.pools import connections

from idm_auth.onboarding.models import PendingActivation
from idm_auth.tests.utils import IDMAuthDaemonTestCaseMixin, GeneratesMessage


class ActivationTestCase(IDMAuthDaemonTestCaseMixin, TestCase):
    def setUp(self):
        self.broker = connections[Connection(hostname=settings.BROKER_HOSTNAME,
                                             ssl=settings.BROKER_SSL,
                                             virtual_host=settings.BROKER_VHOST,
                                             userid=settings.BROKER_USERNAME,
                                             password=settings.BROKER_PASSWORD,
                                             transport=settings.BROKER_TRANSPORT)]
        super().setUp()

    def test_new_established_identity(self):
        identity_id = uuid.uuid4()
        exchange = kombu.Exchange('idm.core.person', 'topic', durable=True)
        with self.broker.acquire(block=True) as conn:
            exchange = exchange(conn)
            exchange.declare()

            message = {
                'state': 'established',
                'emails': [{
                    'context': 'home',
                    'value': 'alice@example.org',
                    'validated': False,
                }]
            }

            with GeneratesMessage('idm.auth.user', timeout=2) as gm:
                exchange.publish(exchange.Message(json.dumps(message).encode(),
                                                  content_type='application/json'),
                                 routing_key='{}.{}.{}'.format('Person',
                                                               'created',
                                                               identity_id))

            self.assertIsInstance(gm.message, Message)
            user = get_user_model().objects.get()
            self.assertEqual(gm.message.delivery_info['routing_key'], 'User.created.{}'.format(user.pk))
            pending_activation = PendingActivation.objects.get()
            self.assertEqual(pending_activation.user, user)