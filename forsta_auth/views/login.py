from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url, redirect
from django.urls import reverse, resolve, Resolver404
from django.utils.functional import cached_property
from django.utils.http import is_safe_url
from social_django.models import Partial

from two_factor.forms import AuthenticationTokenForm
from two_factor.forms import BackupTokenForm
from two_factor.utils import default_device

from two_factor.views.core import LoginView as TwoFactorLoginView

from forsta_auth.exceptions import TwoFactorDisabled
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
        if 'from-social' not in self.request.GET:
            return None
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
            user = user_model.objects.get(pk=self.current_partial.data['kwargs']['user_id'])
        else:
            user = super().get_user()
        return user

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
            'oidc_client': self.get_next_authorize_oidc_client(),
        })
        if self.steps.current == 'auth':
            context.update({
                'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.show], key=lambda sb: sb.name)),
                'awaiting_activation': 'awaiting-activation' in self.request.GET,
            })
        return context

    def get_next_authorize_oidc_client(self):
        """Parses the next redirect URL to discover which OIDC client the user will be authorizing on the next page

        This is opportunistic; if anything it fails silently and returns None.

        A URL of </login/?next=/authorize%3Fclient_id%3Dabcdef%26…> etc will result in the Client with a client_id of
        abcdef being returned.
        """
        if self.redirect_field_name in self.request.GET:
            try:
                resolver_match = resolve(self.request.GET[self.redirect_field_name].split('?', 1)[0])
                if resolver_match.view_name == 'oidc_provider:authorize':
                    query = parse_qs(urlparse(self.request.GET[self.redirect_field_name]).query)
                    # Ensure they've specified one and only one client ID, so that an attacker can't construct a URL
                    # that shows one client name on the login page, and another on the authorize page.
                    if len(query.get('client_id', [])) == 1:
                        from oidc_provider.models import Client
                        return Client.objects.filter(client_id=query['client_id'][0]).first()
            except Resolver404:
                pass

    def dispatch(self, request, *args, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name, '')
        if request.user.is_authenticated and request.user.is_verified():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            return redirect(redirect_to)
        elif 'awaiting-activation' in self.request.GET and redirect_to.split('?')[0].startswith(reverse('signup-done')):
            return redirect(redirect_to)

        return super().dispatch(request, *args, **kwargs)
