import uuid

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from social_core.pipeline.partial import partial
from two_factor.utils import default_device


def add_user_id(user=None, **kwargs):
    # python-social-auth doesn't serialize UUID objects when saving partial pipelines, so we save its UUID as a string
    # here so we can pick it up again.
    if user:
        return {'user_id': str(user.id)}


@partial
def perform_two_factor(user=None, user_id=None, two_factor_complete=False, **kwargs):
    if user and default_device(user) and not two_factor_complete:
        return HttpResponseRedirect(reverse('login'))
    elif not user and user_id and two_factor_complete:
        User = get_user_model()
        return {'user': User.objects.get(id=uuid.UUID(user_id))}
