import uuid

from django.test import TestCase
from django.urls import reverse

from forsta_auth.forms import PasswordSetForm, PasswordChangeForm
from forsta_auth.models import User


class PasswordTestCase(TestCase):
    def testSetWhenUnusable(self):
        user = User(primary=True)
        user.set_unusable_password()
        user.save()

        self.client.force_login(user)
        response = self.client.get(reverse('password-change'))
        self.assertIsInstance(response.context['form'], PasswordSetForm)
        self.assertNotIsInstance(response.context['form'], PasswordChangeForm)

    def testChangeWhenUsable(self):
        password = str(uuid.uuid4())

        user = User(primary=True)
        user.set_password(password)
        user.save()

        self.client.force_login(user)
        response = self.client.get(reverse('password-change'))
        self.assertIsInstance(response.context['form'], PasswordChangeForm)
