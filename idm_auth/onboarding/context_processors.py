from django.conf import settings


def onboarding(request):
    return {
        'ONBOARDING': settings.ONBOARDING,
    }