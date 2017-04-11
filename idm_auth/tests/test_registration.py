from urllib.parse import urljoin

from django.test import TestCase
from django.test import LiveServerTestCase
from selenium import webdriver

class RegistrationTestCase(LiveServerTestCase):
    def setUp(self):
        self.selenium = webdriver.PhantomJS()
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def testNewRegistration(self):
        selenium = self.selenium
        #Opening the link we want to test
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

