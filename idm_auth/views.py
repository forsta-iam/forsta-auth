from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm

from idm_auth.backend_meta import BackendMeta


class LoginView(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        return {
            'form': AuthenticationForm(self.request.POST or None)
        }


class ProfileView(TemplateView):
    template_name = 'profile.html'


    def get_context_data(self, **kwargs):
        return {
            'associated': [BackendMeta(user_social_auth)
                           for user_social_auth in self.request.user.social_auth.all()]
        }
