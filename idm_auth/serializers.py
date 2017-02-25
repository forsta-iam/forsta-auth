from rest_framework import serializers

from . import models

class TypeMixin(object):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['@type'] = self.Meta.model.__name__
        return data


class UserSerializer(TypeMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'username', 'primary', 'identity_id')