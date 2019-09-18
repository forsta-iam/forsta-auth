from django.contrib.auth import views as auth_views

from .. import forms

__all__ = ['PasswordChangeView', 'PasswordChangeDoneView']


class PasswordChangeView(auth_views.PasswordChangeView):
    def get_form_class(self):
        if self.request.user.has_usable_password():
            return forms.PasswordChangeForm
        else:
            return forms.PasswordSetForm


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    pass

