from django.contrib.auth import views as auth_views

from .. import forms

__all__ = ['PasswordChangeView', 'PasswordChangeDoneView']

class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = forms.PasswordChangeForm


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    pass

