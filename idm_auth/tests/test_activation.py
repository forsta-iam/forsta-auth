import json
import unittest.mock
import uuid

import kombu
import time

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from kombu import Connection
from kombu.message import Message
from kombu.pools import connections

from idm_auth.onboarding.models import PendingActivation
from idm_auth.onboarding import tasks as onboarding_tasks
from idm_auth.tests.utils import IDMAuthDaemonTestCaseMixin, GeneratesMessage, update_user_from_identity_noop


@unittest.mock.patch('idm_auth.auth_core_integration.utils.update_user_from_identity', update_user_from_identity_noop)
class ActivationTestCase(IDMAuthDaemonTestCaseMixin, TestCase):
    def setUp(self):
        self.broker = connections[Connection(hostname=settings.BROKER_HOSTNAME,
                                             ssl=settings.BROKER_SSL,
                                             virtual_host=settings.BROKER_VHOST,
                                             userid=settings.BROKER_USERNAME,
                                             password=settings.BROKER_PASSWORD,
                                             transport=settings.BROKER_TRANSPORT)]
        super().setUp()

    @unittest.mock.patch('idm_auth.onboarding.tasks.start_activation')
    def test_new_established_identity(self, start_activation_task):
        # This test ensures that when idm-core creates a new person in the 'established' state, and we didn't previously
        # have a primary user for them, that we create that user and set the activation process in motion.

        identity_id = uuid.uuid4()
        exchange = kombu.Exchange('idm.core.person', 'topic', durable=True)
        with self.broker.acquire(block=True) as conn:
            exchange = exchange(conn)
            exchange.declare()

            message = {
                'state': 'established',
                '@type': 'Person',
                'emails': [{
                    'context': 'home',
                    'value': 'alice@example.org',
                    'validated': False,
                }]
            }

            exchange.publish(exchange.Message(json.dumps(message).encode(),
                                              content_type='application/json'),
                             routing_key='{}.{}.{}'.format('Person',
                                                           'created',
                                                           identity_id))

            # Wait briefly for the PendingActivation to appear
            for i in range(4):
                try:
                    pending_activation = PendingActivation.objects.get()
                    break
                except PendingActivation.DoesNotExist:
                    if i == 3:
                        raise
                    time.sleep(0.5)

            self.assertEqual(pending_activation.identity_id, identity_id)

            start_activation_task.delay.assert_called_once_with(str(pending_activation.id))

    @unittest.mock.patch('idm_auth.auth_core_integration.utils.get_identity_data')
    def test_start_activation_email(self, get_identity_data):
        # Tests whether the start_activation sends an appropriate activation email if the identity has a home contact
        # email address
        identity_id = uuid.uuid4()
        pending_activation = PendingActivation.objects.create(identity_id=identity_id)
        idm_auth_config = apps.get_app_config('idm_auth')

        get_identity_data.return_value = {
            'state': 'established',
            'emails': [{
                'context': 'work',
                'value': 'alice@example.com',
                'validated': True,
            }, {
                'context': 'home',
                'value': 'alice@example.org',
                'validated': False,
            }]
        }
        onboarding_tasks.start_activation(str(pending_activation.id))
        self.assertEqual(get_identity_data.call_count, 1)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.recipients(), ['alice@example.org'])