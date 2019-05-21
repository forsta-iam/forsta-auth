from django.contrib import admin

from . import models


class IDPAdmin(admin.ModelAdmin):
    pass

admin.register(models.IDP, IDPAdmin)