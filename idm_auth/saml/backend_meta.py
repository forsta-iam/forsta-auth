from django.urls import reverse
from idm_auth.backend_meta import BackendMeta


class SAMLBackendMeta(BackendMeta):
    backend_id = 'saml'
    name = 'SAML'
    font_icon = 'fab fa-university'

    @property
    def name(self):
        from social_django.utils import load_backend, load_strategy
        saml_backend = load_backend(
            load_strategy(),
            "saml",
            redirect_uri=reverse('social:complete', args=("saml",))
        )
        return saml_backend.get_idp(self.user_social_auth.uid.split(':')[0]).conf['label']

    @property
    def username(self):
        return '{} at {}'.format(self.user_social_auth.uid.split(':')[1], self.name)
