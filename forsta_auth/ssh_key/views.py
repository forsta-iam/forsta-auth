from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, View, CreateView
from django.views.generic.edit import ProcessFormView, ModelFormMixin

from . import forms, models


class SSHKeyListView(LoginRequiredMixin, ModelFormMixin, ListView, ProcessFormView):
    model = models.SSHKey
    form_class = forms.SSHKeyForm
    object = None

    def get_queryset(self):
        if not self.request.user.primary:
            raise Http404
        return super(SSHKeyListView, self).get_queryset().filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(SSHKeyListView, self).get_form_kwargs()
        kwargs['instance'] = models.SSHKey(user=self.request.user)
        return kwargs

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        return super(SSHKeyListView, self).form_invalid(form)

    def post(self, request):
        if request.POST.get('action') == 'delete':
            for ssh_key in self.get_queryset().filter(id__in=request.POST.getlist('id')):
                ssh_key.delete()
            return redirect(self.get_success_url())
        else:
            return super(SSHKeyListView, self).post(request)

    def get_success_url(self):
        return self.request.build_absolute_uri()

