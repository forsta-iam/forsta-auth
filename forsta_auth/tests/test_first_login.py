from django.test import TestCase


class FirstLoginTestCase(TestCase):
    def testFirstLogin(self):
        response = self.client.get('/login/dummy/')
