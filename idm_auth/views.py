import http.client
from urllib.parse import urljoin

import dateutil.parser
import requests
from django.apps import apps
from django.conf import settings
from django.contrib.auth import load_backend
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.views.core import LoginView as TwoFactorLoginView
from two_factor.utils import default_device

from idm_auth import backend_meta, models
from idm_auth.backend_meta import BackendMeta
from idm_auth.exceptions import ServiceUnavailable
from idm_auth.models import User
from idm_auth.saml.models import IDP


class SocialForm(Form):
    pass

class LoginView(TemplateView):
    # form_list = (
    #     ('auth', AuthenticationForm),
    #     ('social', SocialForm),
    #     ('token', AuthenticationTokenForm),
    #     ('backup', BackupTokenForm),
    # )
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        return {
            'form': AuthenticationForm(self.request.POST or None),
            'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.backend_id != 'saml'], key=lambda sb: sb.name)),
            'idps': IDP.objects.all().order_by('label'),
        }


class SocialTwoFactorLoginView(TwoFactorLoginView):
    form_list = (
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def get_user(self):
        try:
            return User.objects.get(pk=self.request.session['partial_pipeline']['kwargs']['user_id'])
        except KeyError:
            raise Http404

    def done(self, form_list, **kwargs):
        self.request.session['partial_pipeline']['kwargs']['two_factor_complete'] = True
        return HttpResponseRedirect(reverse('social:complete', kwargs={'backend': self.request.session['partial_pipeline']['backend']}))


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


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'idm-auth/index.html'

    def get_context_data(self, **kwargs):
        return {}


class AffiliationListView(LoginRequiredMixin, TemplateView):
    template_name = 'idm-auth/affiliation-list.html'

    state_order = ('offered', 'active', 'suspended', 'pending', 'historic')
    def order_key(self, affiliation):
        try:
            return self.state_order.index(affiliation['state']), affiliation['start_date']
        except IndexError:
            return 100, affiliation['start_date']

    def get_context_data(self, **kwargs):
        url = urljoin(settings.IDM_CORE_URL, '/person/{}/affiliation/'.format(self.request.user.identity_id))
        try:
            response = apps.get_app_config('idm_auth').session.get(url)
            response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError) as e:
            raise ServiceUnavailable from e
        data = response.json()
        affiliations = data['results']
        for affiliation in affiliations:
            for name in ('start_date', 'end_date', 'effective_start_date', 'effective_end_date', 'suspended_until'):
                if affiliation.get(name):
                    affiliation[name] = dateutil.parser.parse(affiliation[name])
        affiliations.sort(key=self.order_key)
        return {
            'affiliations': affiliations,
        }


class ClaimView(TemplateView):
    template_name = 'claim.html'

    def get_context_data(self, activation_code, **kwargs):
        return {
            'user': get_object_or_404(models.User, activation_code=activation_code),
        }


class SAMLMetadataView(View):
    def get(self, request):
        from social.apps.django_app.utils import load_strategy, load_backend
        complete_url = reverse('social:complete', args=("saml",))
        saml_backend = load_backend(
            load_strategy(request),
            "saml",
            redirect_uri=complete_url,
        )
        metadata, errors = saml_backend.generate_metadata_xml()
        if not errors:
            return HttpResponse(content=metadata, content_type='text/xml')
