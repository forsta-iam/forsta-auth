import http.client

from django.http import HttpResponse
from django.test import TestCase


class SAMLTestCase(TestCase):
    def testMetadata(self):
        # Explicit HTTP_HOST, as python-saml2's validate_url doesn't like single-part hosts
        response = self.client.get('/saml-metadata/', HTTP_HOST='testserver.local')
        assert isinstance(response, HttpResponse)
        self.assertEqual(response.status_code, http.client.OK)
        self.assertEqual(response['Content-Type'], 'text/xml')
