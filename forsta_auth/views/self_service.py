from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views import View
from django.views.generic import TemplateView, UpdateView, DetailView
from two_factor.utils import default_device

from forsta_auth import backend_meta
from forsta_auth.backend_meta import BackendMeta

__all__ = ['ProfileView', 'SocialLoginsView', 'IndexView', 'RecoverView']


class IndexView(View):
    template_name = 'idm-auth/index.html'

    def get(self, request):
        return redirect('profile' if request.user.is_authenticated else 'login')


class ProfileView(LoginRequiredMixin, DetailView):
    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'associated': [BackendMeta.wrap(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()],
            'two_factor_default_device': default_device(self.request.user),
            'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.show], key=lambda sb: sb.name)),
        }


class SocialLoginsView(LoginRequiredMixin, TemplateView):
    template_name = 'idm-auth/social-logins.html'

    def get_context_data(self, **kwargs):
        return {
            'associated': [BackendMeta.wrap(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()],
            'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.show], key=lambda sb: sb.name)),
        }


class RecoverView(View):
    pass

