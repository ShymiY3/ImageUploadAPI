from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ["tier"]}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ["tier"]}),)


class ThumbnailInline(admin.StackedInline):
    model = models.Thumbnail
    extra = 1
    
class ImageAdmin(admin.ModelAdmin):
    inlines = [ThumbnailInline]

admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.UserTier)
admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.Thumbnail)