from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from rest_framework import permissions
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from . import models, serializers

AUTH_USER_SERIALIZER = import_string(getattr(settings, 'AUTH_USER_SERIALIZER',
                                             'forsta_auth.serializers.UserSerializer'))


class UserChangeSelfPermission(permissions.DjangoObjectPermissions):
    perms_map = {
        **permissions.DjangoObjectPermissions.perms_map,
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
    }

    def has_permission(self, request, view):
        return True


class UserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = AUTH_USER_SERIALIZER
    queryset = get_user_model().objects.all()
    permission_classes = (UserChangeSelfPermission,)


class UserEmailViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = serializers.UserEmailSerializer
    queryset = models.UserEmail.objects.all()
    permission_classes = (UserChangeSelfPermission,)
