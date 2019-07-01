from django.conf import settings
from django.db import models

from .base_user import AbstractBaseUser

if settings.AUTH_USER_MODEL == 'forsta_auth.User':
    class User(AbstractBaseUser):
        pass


class UserEmail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField(db_index=True, unique=True)
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)

