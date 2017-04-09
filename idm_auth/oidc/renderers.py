import collections
from django.urls import reverse
from rest_framework import renderers
from rest_framework.request import Request


class DjangoOIDCAuthRenderer(renderers.JSONRenderer):
    format = 'django-oidc-auth-json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context['request']
        assert isinstance(request, Request)

        return super().render(collections.OrderedDict([
            ('issuer', request.build_absolute_uri(reverse('index'))),
            ('authorization_endpoint', request.build_absolute_uri(reverse('oidc_provider:authorize'))),
            ('token_endpoint', request.build_absolute_uri(reverse('oidc_provider:token'))),
            ('userinfo_endpoint', request.build_absolute_uri(reverse('oidc_provider:userinfo'))),
            ('jwks_uri', request.build_absolute_uri(reverse('oidc_provider:jwks'))),
            ('client_id', data['client_id']),
            ('client_secret', data.get('client_secret', 'FILL THIS IN')),
        ]), accepted_media_type, renderer_context)