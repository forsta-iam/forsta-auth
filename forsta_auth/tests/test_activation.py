import unittest.mock
import uuid

from django.apps import apps
from django.core import mail
from django.test import TestCase

from forsta_auth.auth_core_integration.tasks import process_person_update
from forsta_auth.onboarding.models import PendingActivation
from forsta_auth.onboarding import tasks as onboarding_tasks
from forsta_auth.tests.utils import update_user_from_identity_noop


@unittest.mock.patch('forsta_auth.auth_core_integration.utils.update_user_from_identity', update_user_from_identity_noop)
class ActivationTestCase(TestCase):
    @unittest.mock.patch('forsta_auth.onboarding.tasks.start_activation')
    def test_new_established_identity(self, start_activation_task):
        identity_id = uuid.uuid4()

        message = {
            'state': 'established',
            '@type': 'Person',
            'emails': [{
                'context': 'home',
                'value': 'alice@example.org',
                'validated': False,
            }]
        }

        process_person_update(body=message,
                              delivery_info={'routing_key': '{}.{}.{}'.format('Person',
                                                                              'created',
                                                                              identity_id)})

        pending_activation = PendingActivation.objects.get()

        self.assertEqual(pending_activation.identity_id, identity_id)

        start_activation_task.delay.assert_called_once_with(str(pending_activation.id))

    @unittest.mock.patch('forsta_auth.auth_core_integration.utils.get_identity_data')
    def test_start_activation_email(self, get_identity_data):
        # Tests whether the start_activation sends an appropriate activation email if the identity has a home contact
        # email address
        identity_id = uuid.uuid4()
        pending_activation = PendingActivation.objects.create(identity_id=identity_id)
        idm_auth_config = apps.get_app_config('forsta_auth')

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