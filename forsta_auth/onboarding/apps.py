from django.apps import AppConfig
from django.db.models.signals import post_save


class OnboardingConfig(AppConfig):
    name = 'forsta_auth.onboarding'

    def ready(self):
        from ..models import User
        from .models import PendingActivation
        post_save.connect(self.user_saved, User)
        post_save.connect(self.pending_activation_saved, PendingActivation)

    def user_saved(self, instance, **kwargs):
        pass #if not instance.id and instance.

    def pending_activation_saved(self, instance, created, **kwargs):
        if created:
            from . import tasks
            tasks.start_activation.delay(str(instance.id))