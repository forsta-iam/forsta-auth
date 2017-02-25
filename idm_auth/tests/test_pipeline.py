import threading
import uuid
from unittest import mock
from unittest.mock import Mock

import kombu
from django.apps import apps
from django.test import TestCase
from kombu.utils import json

from idm_auth.daemon import IDMAuthDaemon
from idm_auth.pipeline.creation import create_user


class CreateUserTestCase(TestCase):
    """Tests our use of our create_user pipeline element in python-social-auth'"""

    def setUp(self):
        self.idm_auth_daemon = IDMAuthDaemon()
        self.idm_auth_daemon_thread = threading.Thread(target=self.idm_auth_daemon)
        self.idm_auth_daemon_thread.start()

    def tearDown(self):
        self.idm_auth_daemon.should_stop = True
        self.idm_auth_daemon_thread.join()

    def testDoesNothingIfUserFound(self):
        kwargs = {'user': Mock()}
        result = create_user(**kwargs)
        self.assertFalse(result)

    def testCreation(self):
        identity_id = uuid.uuid4()

        def create_identity(*args, **kwargs):
            idm_broker_config = apps.get_app_config('idm_broker')
            with idm_broker_config.broker.acquire(block=True) as conn:
                exchange = kombu.Exchange('idm.core.identity').bind(conn)
                message = exchange.Message(json.dumps({'id': str(identity_id),
                                                       'state': 'active',
                                                       '@type': 'Person'}),
                                           content_type='application/json')
                exchange.publish(message, routing_key='Person.created.{}'.format(str(identity_id)))
            response = mock.Mock()
            response.json.return_value = {'id': str(identity_id)}
            return response

        kwargs = {'details': {'first_name': 'Lewis', 'last_name': 'Carroll', 'email': None}}
        identity_id = uuid.uuid4()
        app_config = apps.get_app_config('idm_auth')
        app_config.session, response = Mock(), Mock()
        app_config.session.post.side_effect = create_identity

        result = create_user(**kwargs)
        self.assertTrue(app_config.session.post.called)