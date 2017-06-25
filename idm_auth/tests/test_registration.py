import json
from urllib.parse import urljoin, urlparse

import kombu
import re
from django.apps import apps
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from kombu.message import Message
from django.test import LiveServerTestCase
from selenium import webdriver

from idm_auth.tests.utils import IDMAuthDaemonTestCaseMixin, creates_idm_core_user, GeneratesMessage


class RegistrationTestCase(IDMAuthDaemonTestCaseMixin, LiveServerTestCase):
    test_password = 'ahCoi6shahch5aeViighie6oofiemeim'

    def setUp(self):
        self.selenium = webdriver.PhantomJS()
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    @creates_idm_core_user
    def testNewRegistration(self, identity_id):
        from idm_auth.models import User

        # This is the whole signup flow
        selenium = self.selenium
        selenium.get(urljoin(self.live_server_url, '/signup/'))

        continue_button = selenium.find_element_by_css_selector('input[type=submit]')
        self.assertEqual(continue_button.get_attribute('value'), 'Continue')
        continue_button.click()

        selenium.find_element_by_name('personal-first_name').send_keys('Edgar')
        selenium.find_element_by_name('personal-last_name').send_keys('Poe')
        selenium.find_element_by_name('personal-date_of_birth').send_keys('1809-01-19')
        selenium.find_element_by_name('personal-email').send_keys('edgar@example.org')

        continue_button = selenium.find_element_by_css_selector('input[type=submit]')
        self.assertEqual(continue_button.get_attribute('value'), 'Continue')
        continue_button.click()

        selenium.find_element_by_name('password-password1').send_keys(self.test_password)
        selenium.find_element_by_name('password-password2').send_keys(self.test_password)

        continue_button = selenium.find_element_by_css_selector('input[type=submit]')
        self.assertEqual(continue_button.get_attribute('value'), 'Go')

        with GeneratesMessage('idm.auth.user') as gm:
            continue_button.click()

        self.assertIsInstance(gm.message, Message)
        self.assertTrue(gm.message.delivery_info['routing_key'].startswith('User.created.'))
        self.assertEqual(gm.message.content_type, 'application/json')
        self.assertEqual(json.loads(gm.message.body.decode())['@type'], 'User')

        user = User.objects.get()
        self.assertFalse(user.is_active)
        self.assertIsNone(user.identity_id)
        self.assertEqual(user.first_name, 'Edgar')
        self.assertEqual(user.last_name, 'Poe')
        self.assertEqual(user.email, 'edgar@example.org')

        message = mail.outbox[0]
        assert isinstance(message, EmailMultiAlternatives)
        self.assertEqual(message.subject, 'Activate your Oxford account')

        activation_link = re.search('https://.*', message.body, re.MULTILINE).group(0)
        activation_link = urljoin(self.live_server_url, urlparse(activation_link).path)
        selenium.get(activation_link)
        self.assertEqual(selenium.current_url, urljoin(self.live_server_url, '/activate/complete/'))

        user = User.objects.get()
        self.assertTrue(user.is_active)
        self.assertEqual(user.identity_id, identity_id)
