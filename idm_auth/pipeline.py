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
                                       routing_key='created.*'))

        identity_url = urllib.parse.urljoin(settings.IDENTITY_API_URL, '/identity/')
        identity_id = app_config.session.post(identity_url, {
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
            }]
        }).json()['id']

        while True:
            try:
                message = queue.get(block=True, timeout=10)
            except queue.Empty:
                raise Exception
            message.ack()
            if message.payload['id'] == identity_id:
                break

    kwargs['details'].pop('username', None)
    return {'user': models.User.objects.get(pk=identity_id)}
    import pprint
    pprint.pprint(kwargs)