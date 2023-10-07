from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class ThumbnailInline(admin.StackedInline):
    model = models.Thumbnail
    extra = 0
    readonly_fields = ["thumbnail", 'height']
    
class ImageAdmin(admin.ModelAdmin):
    inlines = [ThumbnailInline]

admin.site.register(models.Image, ImageAdmin)
admin.site.register(models.Thumbnail)