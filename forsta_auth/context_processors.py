from django.conf import settings

from two_factor.utils import default_device


class TwoFactorEnabled(object):
    def __init__(self, request):
        self.request = request

    def __bool__(self):
        try:
            return self._result
        except AttributeError:
            self._result = default_device(self.request.user) is not None
            return self._result


def two_factor_enabled(request):
    return {'two_factor_enabled': TwoFactorEnabled(request)}


def idm_auth(request):
    return {
        'IDM_CORE_URL': settings.IDM_CORE_URL,
    }


def features_enabled(request):
    return {
        'SAML_ENABLED': settings.SAML_ENABLED,
        'KERBEROS_ENABLED': settings.KERBEROS_ENABLED,
        'BROKER_ENABLED': settings.BROKER_ENABLED,
        'SSH_KEYS_ENABLED': settings.SSH_KEYS_ENABLED,
    }
