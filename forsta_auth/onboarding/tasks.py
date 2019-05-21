from urllib.parse import urljoin

from celery import shared_task
from django.apps import apps
from django.conf import settings
from templated_email import send_templated_mail

from . import models

@shared_task
def start_activation(pending_activation_id):
    from ..auth_core_integration.utils import get_identity_data
    pending_activation = models.PendingActivation.objects.get(id=pending_activation_id)
    identity = get_identity_data(pending_activation.identity_id)

    email = None
    for email in identity.get('emails', ()):
        if email['context'] == 'home':
            email = email['value']
            break

    if email:
        start_activation_by_email(pending_activation, identity, email)
    else:
        raise Exception


def start_activation_by_email(pending_activation, identity, email):
    send_templated_mail(
        template_name='onboarding/activation',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        context={
            'identity': identity,
            'pending_activation': pending_activation,
        },
        headers={'X-IDM-Activation-Code': pending_activation.activation_code},
    )
