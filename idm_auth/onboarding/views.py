from django.conf import settings
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView
from registration.backends.hmac.views import RegistrationView, REGISTRATION_SALT
from social_django.models import Partial

from idm_auth.onboarding.forms import PersonalDataForm, WelcomeForm, SetPasswordForm

from .. import models


class SignupView(SessionWizardView):
    template_name = 'onboarding/signup.html'

    form_list = (
        ('welcome', WelcomeForm),
        ('personal', PersonalDataForm),
        ('password', SetPasswordForm),
    )

    def has_password_step(self):
        return self.social_partial is None

    condition_dict = {
        'password': has_password_step,
    }

    @cached_property
    def registration_view(self):
        view = RegistrationView()
        view.request = self.request
        view.get_activation_key = self.get_activation_key
        return view

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.

        """
        return signing.dumps(
            # Wrap username in str(), to handle our UUIDField
            obj=str(getattr(user, user.USERNAME_FIELD)),
            salt=REGISTRATION_SALT
        )

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise PermissionDenied("You cannot sign up for a new account while you are logged in.")
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def social_partial(self):
        if 'partial_pipeline_token' in self.request.session:
            try:
                return Partial.objects.get(token=self.request.session['partial_pipeline_token'])
            except Partial.DoesNotExist:  # pragma: nocover
                return None

    def get_form_initial(self, step):
        if step == 'personal':
            if self.social_partial:
                details = self.social_partial.data['kwargs']['details']
                return {k: details.get(k, '') for k in ['first_name', 'last_name', 'email']}
            else:
                return {}

    def done(self, form_list, form_dict, **kwargs):
        personal_cleaned_data = form_dict['personal'].cleaned_data

        user = models.User(first_name=personal_cleaned_data['first_name'],
                           last_name=personal_cleaned_data['last_name'],
                           email=personal_cleaned_data['email'],
                           date_of_birth=personal_cleaned_data['date_of_birth'].isoformat(),
                           is_active=False,
                           primary=True)
        if form_dict.get('password'):
            user.set_password(form_dict['password'].cleaned_data['password1'])
        user.save()
        self.registration_view.send_activation_email(user)

        if self.social_partial:
            partial = self.social_partial
            partial.data['kwargs']['details'].update({
                'first_name': personal_cleaned_data['first_name'],
                'last_name': personal_cleaned_data['last_name'],
                'email': personal_cleaned_data['email'],
                'date_of_birth': personal_cleaned_data['date_of_birth'].isoformat(),
            })
            partial.data['kwargs'].update({
                'user': str(user.pk),
                'user_details_confirmed': True,

            })
            partial.save()
            return HttpResponseRedirect(
                reverse('social:complete', kwargs={'backend': partial.backend}))
        else:
            return HttpResponseRedirect(
                reverse('signup-done')
            )


class ClaimView(TemplateView):
    template_name = 'onboarding/claim.html'

    def get(self, request, claim_key):
        username = self.validate_key(claim_key)


    def validate_key(self, claim_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or ``None`` if not.

        """
        try:
            username = signing.loads(
                claim_key,
                salt='account-claim',
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return username
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.BadSignature:
            return None
