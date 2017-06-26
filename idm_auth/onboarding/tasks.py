from urllib.parse import urljoin

from celery import shared_task
from django.apps import apps
from django.conf import settings
from templated_email import send_templated_mail

from . import models

@shared_task
def start_activation(id):
    pending_activation = models.PendingActivation.objects.get(id=id)
    session = apps.get_app_config('idm_auth').session

    person_url = urljoin(settings.IDM_CORE_URL, 'person/{}/'.format(pending_activation.user.identity_id))
    response = session.get(person_url)
    response.raise_for_status()

    data = response.json()

    email = None
    for email in data.get('emails', ()):
        if email['context'] == 'home':
            email = email['value']
            break

    if email:
        start_activation_by_email(pending_activation, data, email)
    else:
        raise Exception


def start_activation_by_email(pending_activation, data, email):
    send_templated_mail(
        template_name='onboarding/activation',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        context={
            'identity': data,
            'pending_activation': pending_activation,
        },
        headers={'X-IDM-Activation-Code': pending_activation.activation_code},
    )
