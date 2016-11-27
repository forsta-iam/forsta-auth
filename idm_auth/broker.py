import json
import urllib.parse

from django.apps import apps
from django.conf import settings
from django.db import transaction
from kombu import Connection, Exchange
from kombu.pools import connections

from . import models, serializers

broker_prefix = settings.BROKER_PREFIX

user_exchange = Exchange(broker_prefix + 'user', type='topic')

_config = {
    models.User: (serializers.UserSerializer, user_exchange),
}

class _StubRequest(object):
    def build_absolute_uri(self, path):
        return urllib.parse.urljoin('/', path)

    GET = {}

def init(broker):
    with broker.acquire(block=True) as conn:
        for model, (serializer, exchange) in _config.items():
            bound_exchange = exchange(conn)
            bound_exchange.declare()


def send_message(sender, instance):
    for broker_action in ('deleted', 'created', 'changed'):
        if broker_action in instance._broker_action:
            break
    else:
        return

    serializer, exchange = _config[sender]
    serialiazed = serializer(context={'request': _StubRequest()}).to_representation(instance)

    broker = apps.get_app_config('idm_auth').broker
    with broker.acquire(block=True) as conn:
        bound_exchange = exchange(conn)

        message = bound_exchange.Message(json.dumps(serialiazed),
                                         content_type='application/json')

        bound_exchange.publish(message,
                               routing_key='{}.{}.{}'.format(type(instance).__name__,
                                                             broker_action,
                                                             instance.pk))


def model_changed(sender, instance, created, **kwargs):
    if sender not in _config:
        return

    broker_action = 'created' if created else 'changed'
    try:
        instance._broker_action.add(broker_action)
    except AttributeError:
        instance._broker_action = {broker_action}
    transaction.on_commit(lambda: send_message(sender, instance))


def model_deleted(sender, instance, **kwargs):
    if sender not in _config:
        return

    try:
        instance._broker_action.add('deleted')
    except AttributeError:
        instance._broker_action = {'deleted'}
    transaction.on_commit(lambda: send_message(sender, instance))
