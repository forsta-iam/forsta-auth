from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView as BasePasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views import View
from django.views.generic import TemplateView, UpdateView, DetailView
from two_factor.utils import default_device

from forsta_auth import backend_meta, context_processors, forms
from forsta_auth.backend_meta import BackendMeta

__all__ = ['ProfileView', 'ProfileFormView', 'SocialLoginsView', 'IndexView', 'PasswordResetView']

AUTH_USER_FORM = import_string(getattr(settings, 'AUTH_USER_FORM',
                                       'forsta_auth.forms.ProfileForm'))


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


class ProfileFormView(UpdateView):
    form_class = AUTH_USER_FORM

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('profile')


class SocialLoginsView(LoginRequiredMixin, TemplateView):
    template_name = 'idm-auth/social-logins.html'

    def get_context_data(self, **kwargs):
        return {
            'associated': [BackendMeta.wrap(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()],
            'social_backends': list(sorted([bm for bm in backend_meta.BackendMeta.registry.values() if bm.show], key=lambda sb: sb.name)),
        }


class PasswordResetView(BasePasswordResetView):
    form_class = forms.PasswordResetForm
