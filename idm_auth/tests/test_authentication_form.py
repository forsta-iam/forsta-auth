import uuid

from django.test import TestCase

from idm_auth.forms import AuthenticationForm
from idm_auth.models import User


class AuthenticationFormTestCase(TestCase):
    def testUUID(self):
        user = User(identity_id=uuid.uuid4(), primary=True)
        user.set_password('password')
        user.save()
        form = AuthenticationForm(data={'username': str(user.id), 'password': 'password'})
        self.assertTrue(form.is_valid())
        self.assertEqual(str(user.id), form.cleaned_data['username'])

    def testEmail(self):
        user = User(identity_id=uuid.uuid4(), primary=True, email='alice@example.org')
        user.set_password('password')
        user.save()
        form = AuthenticationForm(data={'username': user.email, 'password': 'password'})
        self.assertTrue(form.is_valid())
        self.assertEqual(str(user.id), form.cleaned_data['username'])

    def testUsername(self):
        user = User(identity_id=uuid.uuid4(), primary=True, username='abcd0123')
        user.set_password('password')
        user.save()
        form = AuthenticationForm(data={'username': user.username, 'password': 'password'})
        self.assertTrue(form.is_valid())
        self.assertEqual(str(user.id), form.cleaned_data['username'])

    def testBadPassword(self):
        user = User(identity_id=uuid.uuid4(), primary=True)
        user.set_password('password')
        user.save()
        form = AuthenticationForm(data={'username': str(user.id), 'password': 'wrongpassword'})
        self.assertFalse(form.is_valid())

    def testBadEmail(self):
        form = AuthenticationForm(data={'username': 'alice@example.org', 'password': 'password'})
        self.assertFalse(form.is_valid())

    def testBadUsername(self):
        form = AuthenticationForm(data={'username': 'alice', 'password': 'password'})
        self.assertFalse(form.is_valid())

    def testEmpty(self):
        form = AuthenticationForm(data={'username': '', 'password': 'password'})
        self.assertFalse(form.is_valid())
