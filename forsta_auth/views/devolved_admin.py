from django.contrib.auth import get_user_model
from django.views.generic import DetailView, ListView

__all__ = ['UserListView', 'UserDetailView']


class UserListView(ListView):
    model = get_user_model()


class UserDetailView(DetailView):
    model = get_user_model()
