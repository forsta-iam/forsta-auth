import uuid

import celery
from celery.utils.log import get_task_logger
from django.db import transaction

from forsta_auth.auth_core_integration.utils import update_user_from_identity

logger = get_task_logger(__name__)


@celery.shared_task(ignore_result=True)
def process_person_update(body, delivery_info, **kwargs):
    from forsta_auth import models
    from forsta_auth.onboarding.models import PendingActivation

    with transaction.atomic(savepoint=False):
        _, action, identity_id = delivery_info['routing_key'].split('.')
        try:
            identity_id = uuid.UUID(identity_id)
        except ValueError:
            logger.exception("Bad identity_id in routing key %s", delivery_info['routing_key'])
            raise
        if action in ('created', 'changed'):
            users = models.User.objects.filter(identity_id=identity_id)
            if not users.exists() and body['@type'] == 'Person' and body['state'] == 'established':
                PendingActivation.objects.get_or_create(identity_id=identity_id)
                logger.info("New Person identity; starting activation process")

            for user in users:
                update_user_from_identity(user, body)
                user.save()
            logger.info("Identity changed")
        elif action == 'deleted':
            for user in models.User.objects.filter(identity_id=identity_id):
                user.delete()
            logger.info("Identity deleted")
        else:
            logger.warning("Unexpected action {} for identity {}".format(action, identity_id))
            raise AssertionError("Unexpected action {} for identity {}".format(action, identity_id))
