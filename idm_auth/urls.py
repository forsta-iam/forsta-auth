from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout
from django.views.generic import TemplateView
from rest_framework import routers

from two_factor.urls import urlpatterns as tf_urls
#from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

import idm_auth.onboarding.views
import idm_auth.oidc.views
import idm_auth.saml.views
from registration.backends.hmac import views as hmac_views
from . import views

router = routers.DefaultRouter()
router.register('oidc/client', idm_auth.oidc.views.ClientViewSet, base_name='client')

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.SocialTwoFactorLoginView.as_view(), name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^recover/$', views.RecoverView.as_view(), name='recover'),
    url(r'^claim/(?P<activation_code>[a-f0-9]{32})/$', views.ClaimView.as_view(), name='claim'),
    url(r'^signup/$', idm_auth.onboarding.views.SignupView.as_view(), name='signup'),
    url(r'^signup/complete/$', TemplateView.as_view(
        template_name='onboarding/signup-done.html'
    ), name='signup-done'),
    url(r'^account/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^account/social-logins/$', views.SocialLoginsView.as_view(), name='social-logins'),

    url(r'^api/', include(router.urls)),

    # Copied from django-registration's HMAC urls
    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='registration_activation_complete'),
    # The activation key can make use of any character from the
    # URL-safe base64 alphabet, plus the colon as a separator.
    url(r'^activate/(?P<activation_key>[-:\w]+)/$',
        hmac_views.ActivationView.as_view(),
        name='registration_activate'),
    url(r'^register/$',
        hmac_views.RegistrationView.as_view(),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'
        ),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ),
        name='registration_disallowed'),
    url(r'', include('registration.auth_urls')),

    url(r'^saml-metadata/$', idm_auth.saml.views.SAMLMetadataView.as_view(), name='saml-metadata'),
    # OpenID Connect
    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    url(r'', include('social_django.urls', namespace='social')),
    url(r'', include(tf_urls, 'two_factor')),
    url(r'^admin/', admin.site.urls),
]
