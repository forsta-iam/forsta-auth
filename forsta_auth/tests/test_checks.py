import smtplib
from unittest import TestCase
from unittest.mock import patch

import requests
from django.core.mail.backends.smtp import EmailBackend
from django.test import override_settings

from forsta_auth import checks as forsta_auth_checks
from forsta_auth.onboarding import checks as onboarding_checks


class OnboardingChecksTestCase(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_check_email_not_smtp(self):
        with patch.object(EmailBackend, 'open') as connection_open:
            self.assertEqual([], onboarding_checks.check_email_config([]))
            self.assertFalse(connection_open.called)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_check_email_good_credentials(self):
        with patch.object(EmailBackend, 'open') as connection_open:
            connection_open.return_value = None
            self.assertEqual([], onboarding_checks.check_email_config([]))
            self.assertTrue(connection_open.called)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
    def test_check_email_bad_credentials(self):
        with patch.object(EmailBackend, 'open') as connection_open:
            connection_open.side_effect = smtplib.SMTPAuthenticationError('550', 'Auth failed')
            self.assertEqual([onboarding_checks.W001], onboarding_checks.check_email_config([]))
            self.assertTrue(connection_open.called)


class SocialCredentialsTestCase(TestCase):
    @override_settings(SOCIAL_AUTH_TWITTER_KEY=None, SOCIAL_AUTH_TWITTER_SECRET=None)
    @patch('requests.post')
    def test_twitter_no_credentials(self, requests_post):
        self.assertEqual([], forsta_auth_checks.check_twitter_credentials([]))
        self.assertFalse(requests_post.called)

    @override_settings(SOCIAL_AUTH_TWITTER_KEY='client-id', SOCIAL_AUTH_TWITTER_SECRET='client-secret')
    @patch('requests.post')
    def test_twitter_good_credentials(self, requests_post):
        self.assertEqual([], forsta_auth_checks.check_twitter_credentials([]))
        self.assertTrue(requests_post.called)

    @override_settings(SOCIAL_AUTH_TWITTER_KEY='client-id', SOCIAL_AUTH_TWITTER_SECRET='client-secret')
    @patch('requests.post')
    def test_twitter_bad_credentials(self, requests_post):
        requests_post.return_value.raise_for_status.side_effect = requests.HTTPError()
        self.assertEqual([forsta_auth_checks.W001], forsta_auth_checks.check_twitter_credentials([]))
        self.assertTrue(requests_post.called)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=None, SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=None)
    @patch('requests.post')
    def test_google_oauth2_no_credentials(self, requests_post):
        self.assertEqual([], forsta_auth_checks.check_google_oauth2_credentials([]))
        self.assertFalse(requests_post.called)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='client-id', SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='client-secret')
    @patch('requests.post')
    def test_google_oauth2_good_credentials(self, requests_post):
        self.assertEqual([], forsta_auth_checks.check_google_oauth2_credentials([]))
        self.assertTrue(requests_post.called)

    @override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='client-id', SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='client-secret')
    @patch('requests.post')
    def test_google_oauth2_bad_credentials(self, requests_post):
        requests_post.return_value.status_code = 401
        self.assertEqual([forsta_auth_checks.W002], forsta_auth_checks.check_google_oauth2_credentials([]))
        self.assertTrue(requests_post.called)
