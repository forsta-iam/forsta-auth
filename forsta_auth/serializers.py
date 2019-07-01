from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models


class TypeMixin(serializers.Serializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['@type'] = self.Meta.model.__name__
        return data


class UserEmailSerializer(TypeMixin, serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:useremail-detail')

    class Meta:
        model = models.UserEmail
        fields = ('id', 'url', 'email', 'verified', 'primary')
        read_only_fields = ('verified',)


class UserSerializer(TypeMixin, serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail')
    # emails = UserEmailSerializer(many=True, required=False)

    if settings.KERBEROS_ENABLED:
        principal_name = serializers.SerializerMethodField()
        def get_principal_name(self, instance):
            return '{}@{}'.format(instance.username, settings.DEFAULT_REALM) if instance.username else None

    class Meta:
        model = get_user_model()
        fields = ('url', 'id', 'username', 'primary', 'identity_id', 'first_name', 'last_name', 'email')
        read_only_fields = ('primary', 'identity_id', 'email')

        if settings.KERBEROS_ENABLED:
            fields += ('principal_name',)
