from django import forms
from django.conf import settings
from django.contrib.auth import password_validation, get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from forsta_auth.onboarding.models import PendingActivation


class WelcomeForm(forms.Form):
    pass


class PersonalDataForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
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
        label=f"Do you already have an existing account with {settings.TEXT_BRANDING['organization_name_in_context']}?",
        coerce=lambda v: v=='yes',
        widget=forms.RadioSelect,
        choices=(('no', 'No'), ('yes', 'Yes')))

class LoginForm(forms.Form):
    pass


class ConfirmActivationForm(forms.Form):
    pass