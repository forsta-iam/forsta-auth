from django.conf import settings
from django.db import models


class SSHKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    label = models.TextField()
    key = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)