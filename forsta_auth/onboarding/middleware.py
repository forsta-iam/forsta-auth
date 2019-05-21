from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from forsta_auth.onboarding.exceptions import RegistrationClosed


class OnboardingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, RegistrationClosed):
            context = {
                'exception': exception,
            }
            return render(request, 'onboarding/signup-closed.html', context, status=503)
