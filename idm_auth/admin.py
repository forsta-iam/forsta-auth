from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from social_django.models import UserSocialAuth

from . import models


class UserSocialAuthInline(admin.TabularInline):
    model = UserSocialAuth
    readonly_fields = fields = ('provider', 'uid')


class UserAdmin(BaseUserAdmin):
    inlines = [
        UserSocialAuthInline,
    ]

admin.site.register(models.User, UserAdmin)