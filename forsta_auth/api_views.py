from rest_framework.viewsets import ModelViewSet

from . import models, serializers


class UserViewSet(ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
