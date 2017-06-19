from celery import shared_task
from django.apps import apps


@shared_task
def sync_user_social_auths(user_id):
    session = apps.get_app_config('idm_auth').session
