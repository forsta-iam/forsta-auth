try:
    import secrets
except ImportError:
    import random
    secrets = random.SystemRandom()
import uuid

from django.conf import settings
from django.db import models


def new_activation_code():
    code = ''.join(secrets.choice(new_activation_code.valid_characters) for i in range(12))
    return ''.join([code[:4], '-', code[4:8], '-', code[8:]])

new_activation_code.valid_characters = 'ABCDEFGHJKMNPRTUVWXY346789'


class PendingActivation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    activation_code = models.CharField(max_length=14, default=new_activation_code, unique=True, db_index=True)
