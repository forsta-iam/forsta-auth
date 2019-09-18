from http.client import FORBIDDEN, SERVICE_UNAVAILABLE

import inflection
import social_core.exceptions
from django.shortcuts import render

from forsta_auth.exceptions import TwoFactorDisabled


class SocialAuthExceptionMiddleware:
    exceptions = {
        social_core.exceptions.NotAllowedToDisconnect: FORBIDDEN,
        social_core.exceptions.AuthAlreadyAssociated: FORBIDDEN,
        social_core.exceptions.AuthCanceled: SERVICE_UNAVAILABLE,
        TwoFactorDisabled: SERVICE_UNAVAILABLE,
    }  # type: Mapping[Exception, int]

    def __init__(self, get_response):
        self.get_response = get_response
        self._template_names = {}

    def __call__(self, request):
        return self.get_response(request)

    def get_template_name_for_exception_class(self, cls):
        if cls not in self._template_names:
            name = '/'.join([
                'exceptions',
                *[n for n in cls.__module__.split('.') if n != 'exceptions'],
                inflection.underscore(cls.__name__) + '.html',
            ])
            self._template_names[cls] = name
        return self._template_names[cls]

    def process_exception(self, request, exception):
        for cls in type(exception).__mro__:
            if cls in self.exceptions:
                return render(
                    request,
                    self.get_template_name_for_exception_class(cls),
                    context={'exception': exception},
                    status=self.exceptions[cls],
                )
