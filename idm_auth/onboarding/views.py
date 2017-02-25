from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from formtools.wizard.views import SessionWizardView

from idm_auth.onboarding.actions import create_identity_and_user
from idm_auth.onboarding.forms import PersonalDataForm, WelcomeForm, SetPasswordForm


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
        if 'partial_pipeline' in self.request.session:
            self.request.session['partial_pipeline']['kwargs']['details'].update({
                'first_name': personal_cleaned_data['first_name'],
                'last_name': personal_cleaned_data['last_name'],
                'email': personal_cleaned_data['email'],
                'date_of_birth': personal_cleaned_data['date_of_birth'].isoformat(),
            })
            self.request.session['partial_pipeline']['kwargs']['user_details_confirmed'] = True
            return HttpResponseRedirect(
                reverse('social:complete', kwargs={'backend': self.request.session['partial_pipeline']['backend']}))
        else:
            user = create_identity_and_user(
                first_name=personal_cleaned_data['first_name'],
                last_name=personal_cleaned_data['last_name'],
                email=personal_cleaned_data['email'],
                date_of_birth=personal_cleaned_data['date_of_birth'],
            )
            user.set_password(form_dict['password'].cleaned_data['password1'])
            user.save()
            raise AssertionError
