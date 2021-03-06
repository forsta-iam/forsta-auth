import uuid

import zxcvbn_password.fields
from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms, get_user_model
from django.utils.translation import ugettext_lazy as _
from two_factor.utils import default_device

from forsta_auth.exceptions import TwoFactorDisabled
from . import models

UserModel = get_user_model()


class AuthenticationForm(auth_forms.AuthenticationForm):
    username = auth_forms.UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': '', 'placeholder': "Username (e.g. 'abcd1234') or email", 'class': 'pure-u-1'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'pure-u-1'}),
    )

    error_messages = auth_forms.AuthenticationForm.error_messages.copy()
    error_messages['inactive'] = _('You need to activate your account before you can log in. Follow the instructions '
                                   'in the email you received, and then try again.')

    def clean(self):
        username = self.cleaned_data.get('username')
        try:
            str(uuid.UUID(username or ''))
        except ValueError:
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                try:
                    user = UserModel.objects.get(emails__email=username)
                except UserModel.DoesNotExist:
                    username = str(uuid.uuid4())
                else:
                    username = str(user.pk)
            else:
                try:
                    UserModel.objects.get(emails__email=username)
                except UserModel.DoesNotExist:
                    pass
                username = str(user.pk)
        self.cleaned_data['username'] = username
        return super().clean()

    def confirm_login_allowed(self, user):
        if not settings.TWO_FACTOR_ENABLED and default_device(user):
            raise TwoFactorDisabled(None)
        return super().confirm_login_allowed(user)


class PasswordSetForm(auth_forms.SetPasswordForm):
    new_password1 = zxcvbn_password.fields.PasswordField(label=_("New password"))
    new_password2 = zxcvbn_password.fields.PasswordConfirmationField(label=_("New password confirmation"),
                                                                     confirm_with='password1')

    # Make the user optional
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)


class PasswordChangeForm(PasswordSetForm, auth_forms.PasswordChangeForm):
    pass


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'username')


class PasswordResetForm(auth_forms.PasswordResetForm):
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This is overridden to also send emails to people that don't have a usable password
        """
        return UserModel.objects.filter(emails__in=models.UserEmail.objects.filter(email__iexact=email, verified=True),
                                        is_active=True).distinct()
