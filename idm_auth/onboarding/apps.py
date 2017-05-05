from django.apps import AppConfig
from django.db.models.signals import post_save


class OnboardingConfig(AppConfig):
    name = 'idm_auth.onboarding'

    def ready(self):
        from ..models import User
        post_save.connect(self.user_saved, User)

    def user_saved(self, instance, **kwargs):
        pass #if not instance.id and instance.