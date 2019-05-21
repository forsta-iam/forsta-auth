from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from forsta_auth.onboarding.models import PendingActivation


class WelcomeForm(forms.Form):
    pass


class PersonalDataForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField()
    email = forms.EmailField()


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