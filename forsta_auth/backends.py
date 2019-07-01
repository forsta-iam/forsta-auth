from django.contrib.auth import get_user_model


class UserSelfBackend:
    def has_perm(self, user_obj, perm, obj=None):
        user_model = get_user_model()
        if not isinstance(obj, user_model):
            return False
        return user_obj == obj
