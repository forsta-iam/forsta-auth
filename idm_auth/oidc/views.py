from rest_framework import viewsets
from oidc_provider import models
from rest_framework.permissions import DjangoModelPermissions

from . import renderers, serializers


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ClientSerializer
    queryset = models.Client.objects.all()
    renderer_classes = [
        renderers.DjangoOIDCAuthRenderer,
        *viewsets.ModelViewSet.renderer_classes,
    ]
    permission_classes = (DjangoModelPermissions,)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
