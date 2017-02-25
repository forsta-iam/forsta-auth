from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout

from two_factor.urls import urlpatterns as tf_urls
#from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

import idm_auth.onboarding.views
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^login/two-factor/$', views.SocialTwoFactorLoginView.as_view(), name='social-two-factor-login'),
    url(r'^claim/(?P<activation_code>[a-f0-9]{32})/$', views.ClaimView.as_view(), name='claim'),
    url(r'^signup/$', idm_auth.onboarding.views.SignupView.as_view(), name='signup'),
    url(r'^account/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^account/social-logins/$', views.SocialLoginsView.as_view(), name='social-logins'),
    url(r'^account/affiliations/$', views.AffiliationListView.as_view(), name='affiliation-list'),
    url(r'^saml-metadata/$', views.SAMLMetadataView.as_view(), name='saml-metadata'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'', include(tf_urls, 'two_factor')),
    url(r'^admin/', admin.site.urls),
]
