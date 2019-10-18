import re
import uuid

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.functional import cached_property

from django.utils.translation import ugettext_lazy as _

from .backend_meta import BackendMeta


if settings.KERBEROS_ENABLED:
    from forsta_auth.kerberos.models import KerberosBackedUserMixin
else:
    class KerberosBackedUserMixin:
        pass


class UsernameValidator(RegexValidator):
    regex = r'^[a-z][a-z0-9_/.\-]+$'
    message = _(
        'Enter a valid username. This value may contain only a-z letters, '
        'numbers, and /_-. characters, and must start with a letter.'
    )
    flags = re.ASCII


class AbstractBaseUser(KerberosBackedUserMixin, DirtyFieldsMixin, AbstractUser):
    username_validator = UsernameValidator()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identity_id = models.UUIDField(db_index=True, null=True, blank=True)
    identity_type = models.CharField(max_length=32, blank=True)

    username = models.CharField(max_length=256, unique=True, null=True, blank=True,
                                validators=[username_validator])
    primary = models.BooleanField(help_text="Whether this is the primary account for the connected resource")

    must_have_password = models.BooleanField(default=False)
    must_have_mfa = models.BooleanField(default=False)
    must_use_password = models.BooleanField(default=False)

    state = models.CharField(max_length=32)

    USERNAME_FIELD = 'id'

    def __repr__(self):
        return '<User {}>'.format(self.id)

    def __str__(self):
        return ' '.join([self.first_name or '', self.last_name or '']).strip()

    def save(self, *args, **kwargs):
        # If there isn't a username, explicitly make it None so that '' doesn't mess up a uniqueness constraint.
        self.username = self.username or None
        return super().save(*args, **kwargs)

    def get_username(self):
        return str(self.id)

    @cached_property
    def social_auth_metas(self):
        return sorted([BackendMeta.wrap(user_social_auth) for user_social_auth in self.social_auth.all()],
                      key=lambda s: (s.backend_id, s.username))

    class Meta:
        abstract = True
