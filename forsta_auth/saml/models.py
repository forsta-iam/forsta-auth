from django.db import models


class IDP(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    label = models.CharField(max_length=256)
    entity_id = models.URLField()
    url = models.URLField()
    x509cert = models.TextField()
