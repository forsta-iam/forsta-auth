from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from social_django.models import UserSocialAuth

from . import models


class UserSocialAuthInline(admin.TabularInline):
    model = UserSocialAuth
    readonly_fields = fields = ('provider', 'uid')
    max_num = 0


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        field_classes = {}


class UserAdmin(BaseUserAdmin):
    inlines = [
        UserSocialAuthInline,
    ]
    form = UserChangeForm

admin.site.register(models.User, UserAdmin)