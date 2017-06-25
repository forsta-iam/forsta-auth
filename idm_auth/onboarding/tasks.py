from urllib.parse import urljoin

from celery import shared_task
from django.apps import apps
from django.conf import settings

from . import models

@shared_task
def start_activation(id):
    pending_activation = models.PendingActivation.objects.get(id=id)
    session = apps.get_app_config('idm_auth').session

    person_url = urljoin(settings.IDM_CORE_URL, 'person/{}/'.format(pending_activation.identity_id))
    response = session.get(person_url)
    response.raise_for_status()

    data = response.json()