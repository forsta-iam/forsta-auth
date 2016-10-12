import kombu
from django.conf import settings
from django.core.management import BaseCommand
from kombu.mixins import ConsumerMixin

amqp_connection = kombu.Connection(settings.BROKER_URL)

identity_queue = kombu.Queue('iam.idm_auth.identity', exchange=kombu.Exchange('iam.idm.identity'))

class Command(ConsumerMixin, BaseCommand):
    def handle(self, *args, **options):
        with kombu.Connection(settings.BROKER_URL) as connection:
            self.connection = connection
            self.run()

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[identity_queue],
                         accept=['json'],
                         callbacks=[self.process_identity],
                         auto_declare=True)]

    def process_identity(self, body, message):
        print(body, message)
