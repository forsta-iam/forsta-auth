import datetime
import urllib

from django.apps import apps
from django.conf import settings
from kombu import Queue

from idm_auth import models
from idm_auth.broker import user_exchange


def create_identity_and_user(first_name, last_name, email, date_of_birth):
    assert isinstance(first_name, str)
    assert isinstance(last_name, str)
    assert isinstance(email, str)
    assert isinstance(date_of_birth, datetime.date)

    app_config = apps.get_app_config('idm_auth')
    broker_app_config = apps.get_app_config('idm_broker')

    with broker_app_config.broker.acquire(block=True) as conn:
        queue = conn.SimpleQueue(Queue(exclusive=True,
                                       exchange=user_exchange,
                                       routing_key='User.created.*'))

        identity_url = urllib.parse.urljoin(settings.IDM_CORE_URL, '/person/')
        data = {
            'names': [{
                'contexts': ['presentational'],
                'components': [{
                    'type': 'given',
                    'value': first_name,
                }, {
                    'type': 'family',
                    'value': last_name,
                }]
            }],
            'emails': [{
                'context': 'home',
                'value': email,
            }],
            'date_of_birth': date_of_birth.isoformat(),
            'state': 'active',
        }
        response = app_config.session.post(identity_url, data)
        print(repr(date_of_birth), data, response.json())
        response.raise_for_status()
        identity_id = response.json()['id']

        while True:
            try:
                message = queue.get(block=True, timeout=2)
            except queue.Empty:
                raise Exception
            message.ack()
            if message.payload['identity_id'] == identity_id:
                break

    return models.User.objects.get(identity_id=identity_id)
