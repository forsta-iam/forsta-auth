from urllib.parse import urlencode, urljoin

from django.apps import apps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView
from django_registration.backends.activation.views import RegistrationView, REGISTRATION_SALT, \
    ActivationView as BaseActivationView
from django_registration.exceptions import ActivationError
from django.utils.translation import ugettext_lazy as _

from formtools.wizard.views import SessionWizardView, NamedUrlCookieWizardView
from social_django.models import Partial

from forsta_auth.auth_core_integration.utils import get_identity_data
from forsta_auth.forms import PasswordSetForm
from forsta_auth.onboarding.forms import PersonalDataForm, WelcomeForm, ActivationCodeForm, \
    ConfirmDetailsForm, ExistingAccountForm, ConfirmActivationForm
from forsta_auth.onboarding.models import PendingActivation
from ..models import UserEmail

CLAIM_SALT = 'forsta_auth.onboarding.claim'


class SocialPipelineMixin(View):
    @cached_property
    def social_partial(self):
        if 'partial_pipeline_token' in self.request.session:
            try:
                return Partial.objects.get(token=self.request.session['partial_pipeline_token'])
            except Partial.DoesNotExist:  # pragma: nocover
                return None

    def delete_social_partial(self):
        if 'partial_pipeline_token' in self.request.session:
            Partial.objects.filter(token=self.request.session['partial_pipeline_token']).delete()
            del self.request.session['partial_pipeline_token']


class SignupView(SocialPipelineMixin, SessionWizardView):
    template_name = 'onboarding/signup.html'

    redirect_field_name = REDIRECT_FIELD_NAME

    form_list = (
        ('welcome', WelcomeForm),
        ('personal', PersonalDataForm),
        ('password', PasswordSetForm),
    )

    def has_welcome_step(self):
        return not self.pending_activation

    def has_personal_step(self):
        return not self.pending_activation

    def has_password_step(self):
        return self.social_partial is None

    condition_dict = {
        'welcome': has_welcome_step,
        'personal': has_personal_step,
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
            obj={'username': str(getattr(user, user.USERNAME_FIELD)),
                 'email': user.email},
            salt=REGISTRATION_SALT
        )

    @cached_property
    def claim(self):
        if 'claim' in self.request.GET:
            return signing.loads(self.request.GET['claim'], salt=CLAIM_SALT, max_age=900)

    @cached_property
    def pending_activation(self):
        if self.claim:
            return PendingActivation.objects.get(activation_code=self.claim['activation_code'])

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise PermissionDenied("You cannot sign up for a new account while you are logged in.")
        if not settings.ONBOARDING['REGISTRATION_OPEN'] and not self.pending_activation:
            return render(request, 'onboarding/signup-closed.html', status=503)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # This ensures that if a user has previously started a social-based signup, but now attempt to sign up by
        # clicking the link, then we shouldn't associate that social login with their new account when it's created;
        # they'll be prompted to set a password instead.
        if 'from-social' not in request.GET:
            self.delete_social_partial()
        return super().get(request, *args, **kwargs)

    def get_form_initial(self, step):
        if step == 'personal':
            if self.social_partial:
                details = self.social_partial.data['kwargs']['details']
                return {k: details.get(k, '') for k in ['first_name', 'last_name', 'email']}
            else:
                return {}

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context.update({
            'pending_activation': self.pending_activation,
            'identity': get_identity_data(self.pending_activation.identity_id) if self.pending_activation else None,
            'redirect_field_name': self.redirect_field_name,
            'redirect_to': self.request.GET.get(self.redirect_field_name),
        })
        return context

    def collapse_redirect_chain(self, redirect_chain):
        redirect_to = redirect_chain[-1]
        for redirect in redirect_chain[-2::-1]:
            redirect_to = redirect + ('&' if '?' in redirect else '?') + urlencode({self.redirect_field_name: redirect_to})
        return redirect_to

    def done(self, form_list, form_dict, **kwargs):
        redirect_chain = [reverse('signup-done')]
        if self.redirect_field_name in self.request.GET:
            redirect_chain.append(self.request.GET[self.redirect_field_name])

        if self.pending_activation:
            user = get_user_model()(is_active=False,
                                    primary=True,
                                    identity_id=self.pending_activation.identity_id)
            self.pending_activation.delete()
        else:
            personal_cleaned_data = form_dict['personal'].cleaned_data
            user = get_user_model()(first_name=personal_cleaned_data['first_name'],
                                    last_name=personal_cleaned_data['last_name'],
                                    email=personal_cleaned_data['email'],
                                    is_active=False,
                                    primary=True)

        if form_dict.get('password'):
            user.set_password(form_dict['password'].cleaned_data['new_password1'])
        else:
            user.set_unusable_password()

        user.save()
        self.registration_view.send_activation_email(user)

        if self.social_partial:
            partial = self.social_partial
            partial.data['kwargs']['details'].update({
                'first_name': personal_cleaned_data['first_name'],
                'last_name': personal_cleaned_data['last_name'],
                'email': personal_cleaned_data['email'],
            })
            partial.data['kwargs'].update({
                'user': str(user.pk),
                'user_details_confirmed': True,

            })
            partial.save()

            redirect_chain.insert(0, reverse('social:complete', kwargs={'backend': partial.backend}))
            begin_social_url = reverse('social:begin', kwargs={'backend': partial.backend})
            if partial.backend == 'saml':
                begin_social_url += '?' + urlencode({'idp': partial.kwargs['response']['idp_name']})
            redirect_chain.insert(2, begin_social_url)

        return HttpResponseRedirect(self.collapse_redirect_chain(redirect_chain))


class SignupCompleteView(TemplateView):
    template_name='onboarding/signup-done.html'
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            'redirect_field_name': self.redirect_field_name,
            'redirect_to': self.request.GET.get(self.redirect_field_name),
        })
        return context


class IdentityClaimView(SocialPipelineMixin, NamedUrlCookieWizardView):
    template_name = 'onboarding/activation.html'

    form_list = (
        ('activation-code', ActivationCodeForm),
        ('confirm-details', ConfirmDetailsForm),
        ('existing-account', ExistingAccountForm),
        ('confirm', ConfirmActivationForm),
    )

    def has_existing_account_step(self):
        return not self.request.user.is_authenticated

    condition_dict = {
        'existing-account': has_existing_account_step,
    }

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context.update({
            'pending_activation': self.pending_activation,
            'identity': self.identity_data,
        })
        return context

    def get(self, request, *args, **kwargs):
        if not kwargs.get('step', None):
            return super().get(request, *args, **kwargs)
        elif self.steps.current == 'activation-code' and 'activation_code' in self.request.GET:
            data = MultiValueDict({self.get_form_prefix() + '-activation_code': [self.request.GET['activation_code']]})
            form = self.get_form(step='activation-code', data=data)
            if form.is_valid():
                self.storage.set_step_data('activation-code', self.process_step(form))
                return self.render_next_step(form)
            else:
                return self.render(form)
        elif 'activation_code' in request.GET:
            return self.render_goto_step(self.steps.current)
        elif self.steps.current == 'confirm' and not self.request.user.is_authenticated:
            has_existing_account = self.get_cleaned_data_for_step('existing-account')['existing_account']
            if has_existing_account:
                return redirect(reverse('login') + '?' + urlencode({'next': self.request.build_absolute_uri()}))
            else:
                claim_token = signing.dumps({'activation_code': self.pending_activation.activation_code},
                                            salt=CLAIM_SALT)
                return redirect(reverse('signup') + '?' + urlencode({'claim': claim_token}))
        else:
            return super().get(request, *args, **kwargs)

    @cached_property
    def pending_activation(self):
        activation_code_step_data = self.get_cleaned_data_for_step('activation-code')
        activation_code = activation_code_step_data['activation_code'] if activation_code_step_data else None
        if activation_code:
            return PendingActivation.objects.get(activation_code=activation_code)

    def get_identity_url(self, identity_id):
        return urljoin(settings.IDM_CORE_API_URL, 'person/{}/'.format(identity_id))

    @cached_property
    def identity_data(self):
        if self.pending_activation:
            return get_identity_data(self.pending_activation.identity_id)

    def done(self, form_list, form_dict, **kwargs):
        existing_identity_id = self.request.user.identity_id
        if existing_identity_id:
            session = apps.get_app_config('forsta_auth').session
            response = session.post(urljoin(self.get_identity_url(existing_identity_id), 'merge/'),
                                    data={'id': self.identity_data['id']})
            response.raise_for_status()
        else:
            self.request.user.identity_id = self.identity_data['id']
            self.request.user.save()

        self.pending_activation.delete()

        return render(self.request, 'onboarding/activation-done.html')


class ActivationView(BaseActivationView):
    EMAIL_IN_USE_MESSAGE = _(
        "The email address you're trying to activate is already in use."
    )

    def activate(self, *args, **kwargs):
        username, email = self.validate_key(kwargs.get('activation_key'))
        user = self.get_user(username)
        try:
            UserEmail.objects.create(user=user, email=email, primary=True, verified=True)
        except IntegrityError as e:
            raise ActivationError(
                self.EMAIL_IN_USE_MESSAGE,
                code='email-in-use',
            )
        user.email = email
        user.is_active = True
        user.save()
        return user

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or raising ``ActivationError`` if not.

        """
        try:
            obj = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return obj['username'], obj['email']
        except signing.SignatureExpired:
            raise ActivationError(
                self.EXPIRED_MESSAGE,
                code='expired'
            )
        except signing.BadSignature:
            raise ActivationError(
                self.INVALID_KEY_MESSAGE,
                code='invalid_key',
                params={'activation_key': activation_key}
            )
