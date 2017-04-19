import contextlib
import json
import threading
import time
import uuid
from unittest import mock

import functools
import kombu
from django.apps import apps

from idm_auth.daemon import IDMAuthDaemon


class IDMAuthDaemonTestCaseMixin(object):
    def setUp(self):
        self.idm_auth_daemon = IDMAuthDaemon()
        self.idm_auth_daemon_thread = threading.Thread(target=self.idm_auth_daemon)
        self.idm_auth_daemon_thread.start()
        super().setUp()

    def tearDown(self):
        self.idm_auth_daemon.should_stop = True
        self.idm_auth_daemon_thread.join()
        super().tearDown()


def creates_idm_core_user(f):
    """Function decorator that mocks the idm-core API that creates a user"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        identity_id = uuid.uuid4()

        def create_identity(url, data, *args, **kwargs):
            idm_broker_config = apps.get_app_config('idm_broker')
            with idm_broker_config.broker.acquire(block=True) as conn:
                exchange = kombu.Exchange('idm.core.identity').bind(conn)
                message = exchange.Message(json.dumps({'id': str(identity_id),
                                                       'state': 'active',
                                                       '@type': 'Person',
                                                       'primary_email': data['emails'][0]['value'],
                                                       'primary_name': {
                                                           'first_name': data['names'][0]['components'][0]['value'],
                                                           'last_name': data['names'][0]['components'][2]['value'],
                                                       }}),
                                           content_type='application/json')
                exchange.publish(message, routing_key='Person.created.{}'.format(str(identity_id)))
            response = mock.Mock()
            response.json.return_value = {'id': str(identity_id)}
            return response

        app_config = apps.get_app_config('idm_auth')
        with mock.patch.object(app_config, 'session'):
            response = mock.Mock()
            app_config.session.post.side_effect = create_identity
            return f(identity_id=identity_id, *args, **kwargs)

    return wrapped


class GeneratesMessage(object):
    def __init__(self, exchange_name, routing_key='#'):
        self.exchange_name = exchange_name
        self.routing_key = routing_key

    def __enter__(self):
        idm_broker_config = apps.get_app_config('idm_broker')
        self.conn = idm_broker_config.broker.acquire(block=True)
        self.queue = kombu.Queue(exclusive=True).bind(self.conn)
        self.queue.declare()
        self.queue.bind_to(exchange=kombu.Exchange(self.exchange_name), routing_key=self.routing_key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.message = self.queue.get()
        self.conn.close()