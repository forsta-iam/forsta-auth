import secrets
from urllib.parse import quote

from django.test import TestCase

from oidc_provider.models import Client
from .. import views


class LoginViewTestCase(TestCase):
    def testGetOIDCClient(self):
        client = Client.objects.create(name="Test Client", client_id=secrets.token_hex(8))

        url = '/login/?next=' + quote('/authorize/?client_id=' + quote(client.client_id))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(client, response.context['oidc_client'])
        self.assertContains(response, '<h1>Log in to Test Client</h1>')

    def testGetOIDCClientWithMissingClientID(self):
        client = Client.objects.create(name="Test Client", client_id=secrets.token_hex(8))

        url = '/login/?next=' + quote('/authorize/?not_client_id=' + quote(client.client_id))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.context['oidc_client'])
        self.assertContains(response, '<h1>Log in</h1>')

    def testGetOIDCClientWithMissingPage(self):
        client = Client.objects.create(name="Test Client", client_id=secrets.token_hex(8))

        url = '/login/?next=' + quote('/missing-page/?client_id=' + quote(client.client_id))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.context['oidc_client'])
        self.assertContains(response, '<h1>Log in</h1>')

    def testGetOIDCClientWithOtherPage(self):
        client = Client.objects.create(name="Test Client", client_id=secrets.token_hex(8))

        url = '/login/?next=' + quote('/reset-password/?client_id=' + quote(client.client_id))
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.context['oidc_client'])
        self.assertContains(response, '<h1>Log in</h1>')

