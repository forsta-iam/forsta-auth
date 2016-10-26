from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from two_factor.utils import default_device

from idm_auth import backend_meta, models
from idm_auth.backend_meta import BackendMeta


class LoginView(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        return {
            'form': AuthenticationForm(self.request.POST or None),
            'social_backends': list(sorted(backend_meta.BackendMeta.registry.values(), key=lambda sb: sb.name)),
        }


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        return {
            'associated': [BackendMeta.wrap(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()],
            'two_factor_default_device': default_device(self.request.user),
            'social_backends': list(sorted(backend_meta.BackendMeta.registry.values(), key=lambda sb: sb.name)),
        }


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        return {}


class ClaimView(TemplateView):
    template_name = 'claim.html'

    def get_context_data(self, activation_code, **kwargs):
        return {
            'user': get_object_or_404(models.User, activation_code=activation_code),
        }