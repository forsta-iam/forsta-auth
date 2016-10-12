from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', admin.site.urls),
]
