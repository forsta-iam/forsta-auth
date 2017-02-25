import urllib.parse

import dateutil.parser
from django.http import HttpResponseRedirect
from django.urls import reverse
from social.pipeline.partial import partial

from idm_auth.onboarding.actions import create_identity_and_user


@partial
def confirm_user_details(user=None, user_details_confirmed=False, **kwargs):
    if user or user_details_confirmed:
        return

    return HttpResponseRedirect(reverse('signup'))


def create_user(**kwargs):
    if kwargs.get('user'):
        return

    kwargs['details'].pop('username', None)
    user = create_identity_and_user(first_name=kwargs['details']['first_name'],
                                    last_name=kwargs['details']['last_name'],
                                    email=kwargs['details']['email'],
                                    date_of_birth=dateutil.parser.parse(kwargs['details']['date_of_birth']).date())

    return {'user': user}
