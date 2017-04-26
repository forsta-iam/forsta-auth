from urllib.parse import urljoin

from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver

from idm_auth.models import User
from idm_auth.tests.utils import IDMAuthDaemonTestCaseMixin


class SocialAuthTestCase(IDMAuthDaemonTestCaseMixin, LiveServerTestCase):
    def setUp(self):
        self.selenium = webdriver.PhantomJS()
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def testDummyNewcomer(self):
        selenium = self.selenium
        selenium.get(urljoin(self.live_server_url, reverse('social:begin', kwargs={'backend': 'dummy'})) +
                     '?first_name=Alice&last_name=Hacker&email=alice@example.org&id=alice')
        self.assertEqual(selenium.current_url,
                         urljoin(self.live_server_url, reverse('signup')))

        continue_button = selenium.find_element_by_css_selector('input[type=submit]')
        self.assertEqual(continue_button.get_attribute('value'), 'Continue')
        continue_button.click()

        self.assertEqual(selenium.find_element_by_name('personal-first_name').get_attribute('value'), 'Alice')
        self.assertEqual(selenium.find_element_by_name('personal-last_name').get_attribute('value'), 'Hacker')
        selenium.find_element_by_name('personal-date_of_birth').send_keys('1809-01-19')
        self.assertEqual(selenium.find_element_by_name('personal-email').get_attribute('value'), 'alice@example.org')
        selenium.find_element_by_name('personal-email').clear()
        selenium.find_element_by_name('personal-email').send_keys('eve@example.org')

        continue_button = selenium.find_element_by_css_selector('input[type=submit]')
        self.assertEqual(continue_button.get_attribute('value'), 'Go')
        continue_button.click()

        user = User.objects.get()
        self.assertFalse(user.is_active)
        self.assertIsNone(user.identity_id)
        self.assertEqual(user.first_name, 'Alice')
        self.assertEqual(user.last_name, 'Hacker')
        self.assertEqual(user.email, 'eve@example.org')
