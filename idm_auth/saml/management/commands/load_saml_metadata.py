import sys
from django.core.management import BaseCommand
from lxml import etree

from idm_auth.saml.models import IDP


class Command(BaseCommand):
    def handle(self, **opts):
        metadata = etree.parse(sys.stdin)
        NS = {'namespaces': {'saml': 'urn:oasis:names:tc:SAML:2.0:metadata',
                             'ds': 'http://www.w3.org/2000/09/xmldsig#',
                             'mdattr': 'urn:oasis:names:tc:SAML:metadata:attribute',
                             'assertion': 'urn:oasis:names:tc:SAML:2.0:assertion'}}
        idp_descriptors = metadata.xpath('''
            //saml:EntityDescriptor[
                not(
                    saml:Extensions/mdattr:EntityAttributes/assertion:Attribute[
                        @Name="http://macedir.org/entity-category" and
                        assertion:AttributeValue/text()='http://refeds.org/category/hide-from-discovery'
                    ]
                ) and
                @ID and
                saml:IDPSSODescriptor[
                    saml:SingleSignOnService[
                        @Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"]]]''', **NS)
        seen_idp_names = set()
        for idp_descriptor in idp_descriptors:
            print(idp_descriptor.attrib)
            try:
                idp = IDP.objects.get(name=idp_descriptor.attrib['ID'])
            except IDP.DoesNotExist:
                idp = IDP(name=idp_descriptor.attrib['ID'])
            seen_idp_names.add(idp.name)
            idp.entity_id = idp_descriptor.attrib['entityID']
            idp.label = idp_descriptor.xpath('saml:Organization/saml:OrganizationDisplayName/text()', **NS)[0]
            idp.url = idp_descriptor.xpath('saml:IDPSSODescriptor/saml:SingleSignOnService[@Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"]/@Location', **NS)[0]
            idp.x509cert = idp_descriptor.xpath('saml:IDPSSODescriptor/saml:KeyDescriptor[@use="signing"]//ds:X509Certificate/text()', **NS)[0]
            idp.save()

        IDP.objects.exclude(name__in=seen_idp_names).delete()