from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, resolve_url, redirect
from django.urls import reverse
from django.utils.http import is_safe_url
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.views import login as auth_login
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.views.core import LoginView as TwoFactorLoginView
from two_factor.utils import default_device

from idm_auth import backend_meta, models
from idm_auth.backend_meta import BackendMeta
from idm_auth.forms import AuthenticationForm
from idm_auth.models import User
from idm_auth.saml.models import IDP


def login(request):
    extra_context = {
        'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.backend_id != 'saml'], key=lambda sb: sb.name)),
        'idps': IDP.objects.all().order_by('label'),
    }
    return auth_login(request,
                      authentication_form=AuthenticationForm,
                      extra_context=extra_context,
                      redirect_authenticated_user=True)


class SocialTwoFactorLoginView(TwoFactorLoginView):
    template_name = 'registration/login.html'
    form_list = (
        ('auth', AuthenticationForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def has_auth_step(self):
        return 'partial_pipeline' not in self.request.session

    condition_dict = {
        'auth': has_auth_step,
        **TwoFactorLoginView.condition_dict
    }

    def get_user(self):
        try:
            return User.objects.get(pk=self.request.session['partial_pipeline']['kwargs']['user_id'])
        except KeyError:
            return super().get_user()

    def done(self, form_list, **kwargs):
        try:
            self.request.session['partial_pipeline']['kwargs']['two_factor_complete'] = True
            return HttpResponseRedirect(reverse('social:complete', kwargs={'backend': self.request.session['partial_pipeline']['backend']}))
        except KeyError:
            return super().done(form_list, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        if self.steps.current == 'auth':
            context.update({
                'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.backend_id != 'saml'], key=lambda sb: sb.name)),
                'idps': IDP.objects.all().order_by('label'),
            })
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified():
            redirect_to = self.request.GET.get(self.redirect_field_name, '')
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            return redirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'idm-auth/profile.html'

    def get_context_data(self, **kwargs):
        return {
            'associated': [BackendMeta.wrap(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()],
            'two_factor_default_device': default_device(self.request.user),
            'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.backend_id != 'saml'], key=lambda sb: sb.name)),
        }


class SocialLoginsView(LoginRequiredMixin, TemplateView):
    template_name = 'idm-auth/social-logins.html'

    def get_context_data(self, **kwargs):
        return {
            'associated': [BackendMeta.wrap(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()],
            'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.backend_id != 'saml'], key=lambda sb: sb.name)),
        }


class IndexView(TemplateView):
    template_name = 'idm-auth/index.html'

    def get_context_data(self, **kwargs):
        return {}


class ClaimView(TemplateView):
    template_name = 'claim.html'

    def get_context_data(self, activation_code, **kwargs):
        return {
            'user': get_object_or_404(models.User, activation_code=activation_code),
        }


class RecoverView(View):
    pass
