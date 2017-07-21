from urllib.parse import urljoin, urlencode

from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver

from idm_auth.models import User


class SocialAuthTestCase(LiveServerTestCase):
    def setUp(self):
        self.selenium = webdriver.PhantomJS()
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def testDummyNewcomer(self):
        begin_dummy_login_url = reverse('social:begin', kwargs={'backend': 'dummy'})
        selenium = self.selenium
        selenium.get(urljoin(self.live_server_url, begin_dummy_login_url +
                     '?first_name=Alice&last_name=Hacker&email=alice@example.org&id=alice'))
        self.assertEqual(selenium.current_url,
                         urljoin(self.live_server_url, reverse('signup')))

        continue_button = selenium.find_element_by_css_selector('button.pure-button-primary')
        self.assertEqual(continue_button.text, 'Continue')
        continue_button.click()

        self.assertEqual(selenium.find_element_by_name('personal-first_name').get_attribute('value'), 'Alice')
        self.assertEqual(selenium.find_element_by_name('personal-last_name').get_attribute('value'), 'Hacker')
        selenium.find_element_by_name('personal-date_of_birth').send_keys('1809-01-19')
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
