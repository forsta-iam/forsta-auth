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