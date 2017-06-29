from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from idm_auth.onboarding.models import PendingActivation


class WelcomeForm(forms.Form):
    pass


class PersonalDataForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField()
    email = forms.EmailField()


class SetPasswordForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        password_validation.validate_password(self.cleaned_data.get('password2'))
        return password2


class ActivationCodeForm(forms.Form):
    activation_code = forms.CharField(label='Activation code')

    def clean_activation_code(self):
        value = self.cleaned_data['activation_code']
        if not PendingActivation.objects.filter(activation_code__iexact=value).exists():
            raise ValidationError("Invalid activation code")
        return value.upper()


class ConfirmDetailsForm(forms.Form):
    pass


class ExistingAccountForm(forms.Form):
    existing_account = forms.TypedChoiceField(
        label="Do you already have an existing account with the University of Oxford?",
        coerce=lambda v: v=='yes',
        widget=forms.RadioSelect,
        choices=(('no', 'No'), ('yes', 'Yes')))

class LoginForm(forms.Form):
    pass


class ConfirmActivationForm(forms.Form):
    pass