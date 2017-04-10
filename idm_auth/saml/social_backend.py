from social_core.backends.saml import SAMLAuth as BaseSAMLAuth, SAMLIdentityProvider

from idm_auth.saml.models import IDP


class SAMLAuth(BaseSAMLAuth):
    def get_idp(self, idp_name):
        idp = IDP.objects.get(name=idp_name)
        return SAMLIdentityProvider(idp.name, **{
            'label': idp.label,
            'entity_id': idp.entity_id,
            'url': idp.url,
            'x509cert': idp.x509cert,
        })