from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.http import is_safe_url
from social_django.models import Partial

from idm_auth.saml.models import IDP
from two_factor.forms import AuthenticationTokenForm
from two_factor.forms import BackupTokenForm

from two_factor.views.core import LoginView as TwoFactorLoginView

from .. import backend_meta, forms

__all__ = ['SocialTwoFactorLoginView']

class SocialTwoFactorLoginView(TwoFactorLoginView):
    template_name = 'registration/login.html'
    form_list = (
        ('auth', forms.AuthenticationForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    @cached_property
    def current_partial(self):
        try:
            return Partial.objects.get(token=self.request.session['partial_pipeline_token'])
        except (KeyError, Partial.DoesNotExist):
            return None

    def has_auth_step(self):
        return self.current_partial is None or 'user_id' not in self.current_partial.data['kwargs']

    condition_dict = TwoFactorLoginView.condition_dict.copy()
    condition_dict['auth'] = has_auth_step

    def get_user(self):
        if self.current_partial and 'user_id' in self.current_partial.data['kwargs']:
            user_model = get_user_model()
            return user_model.objects.get(pk=self.current_partial.data['kwargs']['user_id'])
        else:
            return super().get_user()

    def done(self, form_list, **kwargs):
        if self.current_partial:
            self.current_partial.data['kwargs']['two_factor_complete'] = True
            self.current_partial.save()
            return HttpResponseRedirect(reverse('social:complete', kwargs={'backend': self.current_partial.backend}))
        else:
            return super().done(form_list, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        context.update({
            'redirect_field_name': self.redirect_field_name,
            'redirect_to': self.request.GET.get(self.redirect_field_name),
        })
        if self.steps.current == 'auth':
            context.update({
                'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.backend_id != 'saml'], key=lambda sb: sb.name)),
                'idps': IDP.objects.all().order_by('label'),
                'awaiting_activation': 'awaiting-activation' in self.request.GET,
            })
        return context

    def dispatch(self, request, *args, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name, '')
        if request.user.is_authenticated and request.user.is_verified():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            return redirect(redirect_to)
        elif 'awaiting-activation' in self.request.GET and redirect_to.split('?')[0].startswith(reverse('signup-done')):
            return redirect(redirect_to)

        return super().dispatch(request, *args, **kwargs)
