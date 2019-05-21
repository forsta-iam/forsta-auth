from django.views.generic import DetailView, ListView

from .. import models

__all__ = ['UserListView', 'UserDetailView']

class UserListView(ListView):
    model = models.User


class UserDetailView(DetailView):
    model = models.User
