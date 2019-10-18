import secrets
from unittest import mock

from django.test import TestCase

from .. import backend_meta


class LinkedInTestCase(TestCase):
    def setUp(self):
        self.social_auth = mock.Mock()
        self.social_auth.uid = secrets.token_hex(4)
        self.social_auth_meta = backend_meta.LinkedinBackendMeta(self.social_auth)

    def test_username(self):
        self.assertEqual(None, self.social_auth_meta.username)

    def test_profile_url(self):
        self.assertEqual(None, self.social_auth_meta.profile_url)

