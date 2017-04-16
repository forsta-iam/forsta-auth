import uuid

import re
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


def get_uuid():
    return uuid.uuid4()


class UsernameValidator(RegexValidator):
    regex = r'^[a-z][a-z0-9_/.]+$'
    message = _(
        'Enter a valid username. This value may contain only a-z letters, '
        'numbers, and /_. characters, and must start with a letter.'
    )
    flags = re.ASCII


class User(AbstractUser):
    username_validator = UsernameValidator()

    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    identity_id = models.UUIDField(db_index=True, null=True, blank=True)
    username = models.CharField(max_length=256, unique=True, null=True, blank=True,
                                validators=[username_validator])
    primary = models.BooleanField(help_text="Whether this is the primary account for the connected resource")

    must_have_password = models.BooleanField(default=False)
    must_have_mfa = models.BooleanField(default=False)
    must_use_password = models.BooleanField(default=False)

    state = models.CharField(max_length=32)
    date_of_birth = models.DateField()

    USERNAME_FIELD = 'id'

    def __str__(self):
        return '<User {}>'.format(self.id)

    def get_username(self):
        return str(self.id)
