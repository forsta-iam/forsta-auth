from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView

from two_factor.utils import default_device

from forsta_auth import backend_meta
from forsta_auth.backend_meta import BackendMeta

__all__ = ['ProfileView', 'SocialLoginsView', 'IndexView', 'RecoverView']


class IndexView(TemplateView):
    template_name = 'idm-auth/index.html'

    def get_context_data(self, **kwargs):
        return {}


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


class RecoverView(View):
    pass

