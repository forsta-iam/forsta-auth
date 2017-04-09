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

    def clean_username(self):
        value = self.cleaned_data['username']
        try:
            return str(uuid.UUID(value))
        except ValueError:
            pass
        try:
            user = models.User.objects.get(username=value)
        except models.User.DoesNotExist:
            try:
                user = models.User.objects.get(email=value)
            except models.User.DoesNotExist:
                pass
            else:
                return str(user.pk)
        else:
            try:
                models.User.objects.get(email=value)
            except models.User.DoesNotExist:
                pass
            return str(user.pk)

        return str(uuid.uuid4())