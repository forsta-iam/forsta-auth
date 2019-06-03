import hashlib
import uuid

from oidc_provider import models
from rest_framework import serializers


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    redirect_uris = serializers.ListField(serializers.CharField())
    post_logout_redirect_uris = serializers.ListField(serializers.CharField())

    client_id = serializers.CharField(default=lambda: hashlib.sha224(uuid.uuid4().hex.encode()).hexdigest())

    class Meta:
        model = models.Client
        fields = ('url', 'name', 'client_type', 'client_id', 'response_type', 'jwt_alg', 'date_created', 'website_url',
                  'terms_url', 'contact_email', 'logo', 'redirect_uris', 'post_logout_redirect_uris')

    def create(self, validated_data):
        validated_data['client_secret'] = hashlib.sha224(uuid.uuid4().hex.encode()).hexdigest()
        client = super().create(validated_data)
        client.just_created = True
        return client

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if getattr(instance, 'just_created', False):
            data['client_secret'] = instance.client_secret
        return data
