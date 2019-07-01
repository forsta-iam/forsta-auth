import copy
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from social_django.models import UserSocialAuth

from . import models
from django.utils.translation import ugettext_lazy as _


class UserSocialAuthInline(admin.TabularInline):
    model = UserSocialAuth
    readonly_fields = fields = ('provider', 'uid')
    max_num = 0


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        field_classes = {}


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'identity_id', 'identity_type', 'is_active',
                    'is_staff', 'is_superuser', 'primary')
    add_fieldsets = copy.deepcopy(BaseUserAdmin.add_fieldsets)
    add_fieldsets[0][1]['fields'] += ('identity_id', 'primary')

    inlines = [
        UserSocialAuthInline,
    ]
    form = UserChangeForm
    fieldsets = BaseUserAdmin.fieldsets[:1] + (
        (_('Identity'), {'fields': ('identity_id', 'primary')}),
    ) + BaseUserAdmin.fieldsets[1:]
    #readonly_fields = BaseUserAdmin.readonly_fields + ('identity_id', 'primary')

admin.site.register(get_user_model(), UserAdmin)
