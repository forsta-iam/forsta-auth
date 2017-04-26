from django.http import HttpResponse
from django.urls import reverse
from django.views import View


class SAMLMetadataView(View):
    def get(self, request):
        from social_django.utils import load_strategy, load_backend
        complete_url = reverse('social:complete', args=("saml",))
        saml_backend = load_backend(
            load_strategy(request),
            "saml",
            redirect_uri=complete_url,
        )
        metadata, errors = saml_backend.generate_metadata_xml()
        if not errors:
            return HttpResponse(content=metadata, content_type='text/xml')
