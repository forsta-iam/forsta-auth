import uuid

from django import forms
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm, UsernameField
from django.utils.translation import ugettext_lazy as _

from . import models


class AuthenticationForm(BaseAuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': '', 'placeholder': "Username (e.g. 'abcd1234') or email", 'class': 'pure-u-1'}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'pure-u-1'}),
    )

    error_messages = {**BaseAuthenticationForm.error_messages,
                      'inactive': _('You need to activate your account before you can log in. Follow the instructions '
                                    'in the email you received, and then try again.')}

    def clean(self):
        username = self.cleaned_data.get('username')
        try:
            str(uuid.UUID(username or ''))
        except ValueError:
            try:
                user = models.User.objects.get(username=username)
            except models.User.DoesNotExist:
                try:
                    user = models.User.objects.get(email=username)
                except models.User.DoesNotExist:
                    username = str(uuid.uuid4())
                else:
                    username = str(user.pk)
            else:
                try:
                    models.User.objects.get(email=username)
                except models.User.DoesNotExist:
                    pass
                username = str(user.pk)
        self.cleaned_data['username'] = username
        return super().clean()
