from forsta_auth.saml.models import IDP


def idps(request):
    return {
        'idps': lambda: IDP.objects.all().order_by('label'),
    }
