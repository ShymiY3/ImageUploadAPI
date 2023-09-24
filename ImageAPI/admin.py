from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ["tier"]}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ["tier"]}),)


admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.UserTier)
admin.site.register(models.Image)