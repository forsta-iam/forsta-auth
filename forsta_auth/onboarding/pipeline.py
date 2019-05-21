from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from social_core.pipeline.partial import partial

from . import exceptions


@partial
def confirm_user_details(user=None, user_details_confirmed=False, backend=None, **kwargs):
    if not user and not settings.ONBOARDING['REGISTRATION_OPEN']:
        raise exceptions.RegistrationClosed(backend)
    elif not user and backend.name == 'saml' and not settings.ONBOARDING['REGISTRATION_OPEN_SAML']:
        raise exceptions.SAMLRegistrationClosed(backend)
    elif not user and not settings.ONBOARDING['REGISTRATION_OPEN_SOCIAL']:
        raise exceptions.SocialRegistrationClosed(backend)

    if user or user_details_confirmed:
        return

    return HttpResponseRedirect(reverse('signup'))
