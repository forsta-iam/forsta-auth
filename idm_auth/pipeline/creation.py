import dateutil.parser
from django.http import HttpResponseRedirect
from django.urls import reverse
from social_core.pipeline.partial import partial

from idm_auth.onboarding.actions import create_identity_and_user


@partial
def confirm_user_details(user=None, user_details_confirmed=False, **kwargs):
    if user or user_details_confirmed:
        return

    return HttpResponseRedirect(reverse('signup'))
