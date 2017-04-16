from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView
from registration.backends.hmac.views import RegistrationView, REGISTRATION_SALT

from idm_auth.onboarding.forms import PersonalDataForm, WelcomeForm, SetPasswordForm

from .. import models

class ActivationView(TemplateView):
    def get(self):
        pass


class SignupView(SessionWizardView):
    template_name = 'onboarding/signup.html'

    form_list = (
        ('welcome', WelcomeForm),
        ('personal', PersonalDataForm),
        ('password', SetPasswordForm),
    )

    def has_password_step(self):
        return 'partial_pipeline' not in self.request.session

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
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_initial(self, step):
        if step == 'personal':
            try:
                details = self.request.session['partial_pipeline']['kwargs']['details']
            except KeyError:
                return {}
            else:
                return {k: details.get(k, '') for k in ['first_name', 'last_name', 'email']}

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

        if 'partial_pipeline' in self.request.session:
            self.request.session['partial_pipeline']['kwargs']['details'].update({
                'first_name': personal_cleaned_data['first_name'],
                'last_name': personal_cleaned_data['last_name'],
                'email': personal_cleaned_data['email'],
                'date_of_birth': personal_cleaned_data['date_of_birth'].isoformat(),
                'user': user,
            })
            self.request.session['partial_pipeline']['kwargs']['user_details_confirmed'] = True
            return HttpResponseRedirect(
                reverse('social:complete', kwargs={'backend': self.request.session['partial_pipeline']['backend']}))
        else:
            return HttpResponseRedirect(
                reverse('signup-done')
            )

class SignupDoneView(TemplateView):
    template_name = 'onboarding/signup-done.html'