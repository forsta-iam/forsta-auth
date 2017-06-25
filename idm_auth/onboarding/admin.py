from django.contrib import admin

from . import models


class PendingActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created')

admin.site.register(models.PendingActivation, PendingActivationAdmin)