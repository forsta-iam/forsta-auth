import http.client
import uuid

from django.test import TestCase, override_settings
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice
from social_django.models import UserSocialAuth

from forsta_auth.models import User


class TwoFactorTestCase(TestCase):
    def setUp(self):
        self.password = str(uuid.uuid4())
        self.user = User(username='user', primary=True)
        self.user.set_password(self.password)
        self.user.save()

    @override_settings(TWO_FACTOR_ENABLED=False)
    def testForbid2FAUsersWhen2FADisabledPassword(self):
        device = TOTPDevice.objects.create(user=self.user, name='default', confirmed=True)

        response = self.client.post(reverse('login'), {
            'social_two_factor_login_view-current_step': 'auth',
            'auth-username': self.user.username,
            'auth-password': self.password
        })
        self.assertEqual(http.client.SERVICE_UNAVAILABLE, response.status_code)
        self.assertTemplateUsed(response, 'exceptions/forsta_auth/two_factor_disabled.html')

    @override_settings(TWO_FACTOR_ENABLED=False)
    def testForbid2FAUsersWhen2FADisabledSocial(self):
        device = TOTPDevice.objects.create(user=self.user, name='default', confirmed=True)
        UserSocialAuth.objects.create(user=self.user, provider='dummy', uid='alice')

        response = self.client.get(reverse('social:begin',
                                            kwargs={'backend': 'dummy'}) + '?id=alice',
                                   follow=True)
        self.assertEqual(http.client.SERVICE_UNAVAILABLE, response.status_code)
        self.assertTemplateUsed(response, 'exceptions/forsta_auth/two_factor_disabled.html')
