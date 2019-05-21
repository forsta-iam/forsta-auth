from urllib.parse import urljoin

import requests
import requests_oauthlib
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from oidc_provider.lib.utils.oauth2 import protected_resource_view
from social_django.models import UserSocialAuth


class ProxiedAPIView(View):
    api_url = None
    provider = None
    client_id = None

    discard_request_headers = set(k.lower() for k in {'Host',
                                                      'Authorization',
                                                      'X-Forwarded-For',
                                                      'TE',
                                                      'Accept-Encoding',
                                                      'Cookie',
                                                      'Connection'})
    discard_response_headers = set(k.lower() for k in {'Transfer-Encoding',
                                                       'Content-Encoding',
                                                       'Content-Length',
                                                       'Server',
                                                       'Set-Cookie',
                                                       'Connection',
                                                       'WWW-Authenticate',
                                                       'Keep-Alive',
                                                       'Proxy-Authenticate',
                                                       'Proxy-Authentication',
                                                       'TE',
                                                       'Trailers',
                                                       'Transfer-Encoding',
                                                       'Upgrade'})

    @method_decorator(protected_resource_view())
    def dispatch(self, request, path_info, token):
        api_url = urljoin(self.api_url, path_info) + '?' + request.META.get('QUERY_STRING', '')
        headers = {}
        for k, v in request.META.items():
            if not k.startswith('HTTP_'):
                continue
            k = k[5:].lower().replace('_', '-')
            if k not in self.discard_request_headers:
                headers[k] = v

        usa = UserSocialAuth.objects.get(user=token.user, provider=self.provider)
        token = usa.extra_data

        session = requests_oauthlib.OAuth2Session(client_id=self.client_id,
                                                  token=token)

        upstream_response = session.request(request.method, api_url, headers=headers)
        response = HttpResponse(upstream_response.content, status=upstream_response.status_code)
        for k, v in upstream_response.headers.items():
            if k.lower() not in self.discard_response_headers:
                response[k] = v
        return response