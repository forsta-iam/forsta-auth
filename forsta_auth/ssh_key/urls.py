from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.SSHKeyListView.as_view(), name='list'),
]