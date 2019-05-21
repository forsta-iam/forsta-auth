import urllib.parse

from rest_framework.reverse import reverse
from social_core.backends.base import BaseAuth
from social_core.strategy import BaseStrategy

from forsta_auth.backend_meta import BackendMeta


class DummyBackend(BaseAuth):
    name = 'dummy'
    ID_KEY = 'id'
    REQUIRES_EMAIL_VALIDATION = False
    EXTRA_DATA = []

    def auth_url(self):
        assert isinstance(self.strategy, BaseStrategy)
        request_data = self.strategy.request_data(merge=False)
        return reverse('social:complete', kwargs={'backend': self.name}) + '?' + urllib.parse.urlencode(request_data)

    def auth_complete(self, user=None):
        request_data = self.strategy.request_data(merge=False)
        request_data = {k: request_data[k] for k in request_data}
        kwargs = {'user': user,
                  'backend': self,
                  'strategy': self.strategy,
                  'response': request_data}
        return self.authenticate(**kwargs)

    def get_user_details(self, response):
        return response


class DummyBackendMeta(BackendMeta):
    backend_id = 'dummy'
    name = 'Dummy'
    font_icon = 'fa fa-exclamation-triangle'

BackendMeta.registry[DummyBackendMeta.backend_id] = DummyBackendMeta()