from django.contrib.auth import views as auth_views

from .. import forms

__all__ = ['PasswordChangeView', 'PasswordChangeDoneView', 'PasswordResetConfirmView']


class PasswordChangeView(auth_views.PasswordChangeView):
    def get_form_class(self):
        if self.request.user.has_usable_password():
            return forms.PasswordChangeForm
        else:
            return forms.PasswordSetForm


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    pass


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = forms.PasswordSetForm
    template_name = 'registration/password_change_form.html'
