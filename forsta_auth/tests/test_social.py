import http.client
import unittest.mock
import uuid
from urllib.parse import urljoin, urlencode

from django.test import LiveServerTestCase
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from social_django.models import UserSocialAuth

from forsta_auth.models import User


class SocialAuthTestCase(LiveServerTestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.selenium = webdriver.Chrome(chrome_options=chrome_options)
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def testDummyNewcomer(self):
        begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
        selenium = self.selenium
        selenium.get(urljoin(self.live_server_url, begin_dummy_login_url +
                     '?first_name=Alice&last_name=Hacker&email=alice@example.org&id=alice'))
        self.assertEqual(urljoin(self.live_server_url, reverse('signup') + '?from-social'),
                         selenium.current_url)

        continue_button = selenium.find_element_by_css_selector('button.pure-button-primary')
        self.assertEqual(continue_button.text, 'Continue')
        continue_button.click()

        self.assertEqual(selenium.find_element_by_name('personal-first_name').get_attribute('value'), 'Alice')
        self.assertEqual(selenium.find_element_by_name('personal-last_name').get_attribute('value'), 'Hacker')
        self.assertEqual(selenium.find_element_by_name('personal-email').get_attribute('value'), 'alice@example.org')
        selenium.find_element_by_name('personal-email').clear()
        selenium.find_element_by_name('personal-email').send_keys('eve@example.org')

        continue_button = selenium.find_element_by_css_selector('button.pure-button-primary')
        self.assertEqual(continue_button.text, 'Go')
        continue_button.click()

        self.assertEqual(urljoin(self.live_server_url,
                                 reverse('signup-done') + '?' + urlencode({'next': begin_dummy_login_url})),
                         selenium.current_url)
        self.assertEqual(selenium.find_element_by_css_selector('h1').text, "Account created")

        user = User.objects.get()
        self.assertFalse(user.is_active)
        self.assertIsNone(user.identity_id)
        self.assertEqual(user.first_name, 'Alice')
        self.assertEqual(user.last_name, 'Hacker')
        self.assertEqual(user.email, 'eve@example.org')

    def test_aborted_social_signup(self):
        begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
        selenium = self.selenium
        selenium.get(urljoin(self.live_server_url, begin_dummy_login_url +
                     '?first_name=Alice&last_name=Hacker&email=alice@example.org&id=alice'))
        self.assertEqual(urljoin(self.live_server_url, reverse('signup') + '?from-social'),
                         selenium.current_url)
        # Click past the welcome step
        selenium.find_element_by_css_selector('button.pure-button-primary').click()
        # There shouldn't be a password step, as we're associating a social login
        self.assertEqual(selenium.find_element_by_css_selector('button.pure-button-primary').text, "Go")

        # But now let's start the signup flow afresh
        selenium.get(urljoin(self.live_server_url, reverse('signup')))
        # Click past the welcome step
        selenium.find_element_by_css_selector('button.pure-button-primary').click()
        # There should now be a password step beyond the user details step.
        self.assertEqual(selenium.find_element_by_css_selector('button.pure-button-primary').text, "Continue")


    def test_closed_social_registration(self):
        with self.settings(ONBOARDING={
            'REGISTRATION_OPEN': True,
            'REGISTRATION_OPEN_SOCIAL': False,
            'REGISTRATION_OPEN_SAML': True,
        }):
            begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
            selenium = self.selenium
            selenium.get(urljoin(self.live_server_url, begin_dummy_login_url +
                         '?first_name=Alice&last_name=Hacker&email=alice@example.org&id=alice'))
            self.assertEqual(selenium.find_element_by_css_selector('h1').text, 'Registration closed')

        with self.settings(ONBOARDING={
            'REGISTRATION_OPEN': False,
            'REGISTRATION_OPEN_SOCIAL': True,
            'REGISTRATION_OPEN_SAML': True,
        }):
            begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
            selenium = self.selenium
            selenium.get(urljoin(self.live_server_url, begin_dummy_login_url +
                                 '?first_name=Alice&last_name=Hacker&email=alice@example.org&id=alice'))
            self.assertEqual(selenium.find_element_by_css_selector('h1').text, 'Registration closed')

    @unittest.mock.patch('forsta_auth.auth_core_integration.utils.update_user_from_identity')
    def test_social_with_two_factor(self, update_user_from_identity):
        user = User.objects.create(identity_id=uuid.uuid4(), primary=True)
        user_social_auth = UserSocialAuth.objects.create(user=user, provider='dummy', uid='alice')
        TOTPDevice.objects.create(user=user, name='default', confirmed=True)
        begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
        selenium = self.selenium
        selenium.get(urljoin(self.live_server_url, begin_dummy_login_url + '?id=alice'))
        self.assertEqual(selenium.current_url,
                         urljoin(self.live_server_url, reverse('login')))
        # Make sure we're being asked for a token
        selenium.find_element_by_name('token-otp_token')

    def test_social_signup_then_login(self):
        # If someone attempts to log in with a social account we've not seen before and then visits the login page
        # we shouldn't assume they've got a user. This might happen as they would have a Partial from the
        # not-yet-complete social login
        selenium = self.selenium
        begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
        selenium.get(urljoin(self.live_server_url, begin_dummy_login_url + '?id=alice'))
        # Make sure we got to the signup page
        self.assertEqual(selenium.current_url,
                         urljoin(self.live_server_url, reverse('signup') + '?from-social'))
        # Now attempt to visit the login page
        selenium.get(urljoin(self.live_server_url, reverse('login')))
        self.assertEqual('Log in', selenium.find_element_by_css_selector('h1').text)

    def test_not_allowed_to_disconnect(self):
        user = User(identity_id=uuid.uuid4(), primary=True)
        user.set_unusable_password()
        user.save()
        user_social_auth = UserSocialAuth.objects.create(user=user, provider='dummy', uid='alice')
        self.client.force_login(user)
        response = self.client.post(reverse('social:disconnect_individual',
                                            kwargs={'backend': 'dummy',
                                                    'association_id': user_social_auth.pk}))
        self.assertEqual(http.client.FORBIDDEN, response.status_code)
        self.assertTemplateUsed(response, 'exceptions/social_core/not_allowed_to_disconnect.html')

    def test_auth_already_associated(self):
        alice = User.objects.create(identity_id=uuid.uuid4(), primary=True)
        bob = User.objects.create(identity_id=uuid.uuid4(), primary=True)
        UserSocialAuth.objects.create(user=alice, provider='dummy', uid='alice')
        # Bob is logged in, but tries to associate Alice's social auth with his account
        self.client.force_login(bob)
        response = self.client.get(reverse('social:begin',
                                            kwargs={'backend': 'dummy'}) + '?id=alice',
                                   follow=True)
        self.assertEqual(http.client.FORBIDDEN, response.status_code)
        self.assertTemplateUsed(response, 'exceptions/social_core/auth_already_associated.html')
