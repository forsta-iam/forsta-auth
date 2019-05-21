from django.conf import settings
from rest_framework import serializers

from . import models


class TypeMixin(serializers.Serializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['@type'] = self.Meta.model.__name__
        return data


class UserSerializer(TypeMixin, serializers.HyperlinkedModelSerializer):
    principal_name = serializers.SerializerMethodField()

    def get_principal_name(self, instance):
        return '{}@{}'.format(instance.username, settings.DEFAULT_REALM) if instance.username else None

    class Meta:
        model = models.User
        fields = ('id', 'username', 'primary', 'identity_id', 'principal_name')