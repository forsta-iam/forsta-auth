import urllib.parse

from django.apps import apps
from django.conf import settings
from kombu import Queue

from idm_auth import models
from idm_auth.broker import user_exchange


def create_user(**kwargs):
    if kwargs.get('user'):
        return

    app_config = apps.get_app_config('idm_auth')

    with app_config.broker.acquire(block=True) as conn:
        queue = conn.SimpleQueue(Queue(exclusive=True,
                                       exchange=user_exchange,
                                       routing_key='User.created.*'))

        identity_url = urllib.parse.urljoin(settings.IDM_CORE_URL, '/person/')
        response = app_config.session.post(identity_url, {
            'names': [{
                'contexts': ['presentational'],
                'components': [{
                    'type': 'given',
                    'value': kwargs['details']['first_name'],
                }, {
                    'type': 'family',
                    'value': kwargs['details']['last_name'],
                }]
            }],
            'emails': [{
                'context': 'home',
                'value': kwargs['details']['email'],
            }],
            'state': 'active',
        })
        response.raise_for_status()
        person_id = response.json()['id']

        while True:
            try:
                message = queue.get(block=True, timeout=10)
            except queue.Empty:
                raise Exception
            message.ack()
            if message.payload['person_id'] == person_id:
                break

    kwargs['details'].pop('username', None)
    return {'user': models.User.objects.get(person_id=person_id)}

