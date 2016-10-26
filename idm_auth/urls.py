from django.conf.urls import url, include
from django.contrib import admin

from two_factor.urls import urlpatterns as tf_urls
#from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^claim/(?P<activation_code>[a-f0-9]{32})/$', views.ClaimView.as_view(), name='claim'),
    url(r'^account/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'', include(tf_urls, 'two_factor')),
    url(r'^admin/', admin.site.urls),
]
