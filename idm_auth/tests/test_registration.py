import json
import unittest.mock
import uuid
from urllib.parse import urljoin, urlparse

import re
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from kombu.message import Message
from django.test import LiveServerTestCase, TestCase
from selenium import webdriver

from idm_auth.auth_core_integration.utils import update_user_from_identity
from idm_auth.tests.utils import BrokerTaskConsumerTestCaseMixin, creates_idm_core_user, GeneratesMessage, \
    update_user_from_identity_noop


@unittest.mock.patch('idm_auth.auth_core_integration.utils.update_user_from_identity', update_user_from_identity_noop)
class RegistrationTestCase(BrokerTaskConsumerTestCaseMixin, LiveServerTestCase):
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

        continue_button = selenium.find_element_by_css_selector('button.pure-button-primary')
        self.assertEqual(continue_button.text, 'Continue')
        continue_button.click()

        selenium.find_element_by_name('personal-first_name').send_keys('Edgar')
        selenium.find_element_by_name('personal-last_name').send_keys('Poe')
        selenium.find_element_by_name('personal-date_of_birth').send_keys('1809-01-19')
        selenium.find_element_by_name('personal-email').send_keys('edgar@example.org')

        continue_button = selenium.find_element_by_css_selector('button.pure-button-primary')
        self.assertEqual(continue_button.text, 'Continue')
        continue_button.click()

        selenium.find_element_by_name('password-new_password1').send_keys(self.test_password)
        selenium.find_element_by_name('password-new_password2').send_keys(self.test_password)

        continue_button = selenium.find_element_by_css_selector('button.pure-button-primary')
        self.assertEqual(continue_button.text, 'Go')

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


@unittest.mock.patch('idm_auth.auth_core_integration.utils.update_user_from_identity', update_user_from_identity_noop)
class DuplicateEmailTestCase(TestCase):
    # We let users register with email addresses that might be in use by other people so as not to give away the fact
    # that that person is already registered. When they come to confirm their email address, we tell them to pick a new
    # one.

    @creates_idm_core_user
    def test_duplicate_email_registration_works(self, identity_id):
        from idm_auth.models import User
        user_one = User.objects.create(email='alice@example.org', is_active=False, primary=True)
        user_two = User.objects.create(email='alice@example.org', is_active=False, primary=True)

        user_one.is_active = True
        user_one.save()
        # Email addresses on User are only for activation; they get removed afterwards.
        self.assertEqual(user_one.email, '')

    def test_non_primary_no_email(self):
        identity_id = uuid.uuid4()
        from idm_auth.models import User
        user_one = User.objects.create(identity_id=identity_id, is_active=True, primary=True)
        user_two = User.objects.create(identity_id=identity_id, is_active=True, primary=False)

        identity = {
            'id': str(identity_id),
            '@type': 'Person',
            'state': 'active',
            'emails': [{
                'context': 'home',
                'value': 'alice@example.org',
                'validated': True
            }]
        }

        update_user_from_identity(user_one, identity)
        update_user_from_identity(user_two, identity)

