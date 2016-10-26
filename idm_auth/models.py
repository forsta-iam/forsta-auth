import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


def get_uuid():
    return uuid.uuid4().hex


class User(AbstractUser):
    id = models.CharField(max_length=32, primary_key=True, editable=False)
    username = models.CharField(max_length=256, unique=True, null=True, blank=True)

    state = models.CharField(max_length=32)
    #activation_code = models.UUIDField(null=True, blank=True, unique=True, default=None)

    USERNAME_FIELD = 'id'

    def __str__(self):
        return '<User {}>'.format(self.id)

    def save(self, *args, **kwargs):
            if self.state == 'pending_claim' and not self.activation_code:
            self.activation_code = get_uuid()
        super().save(*args, **kwargs)