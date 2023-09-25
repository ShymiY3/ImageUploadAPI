from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import os

class UserTier(models.Model):
    name = models.CharField(max_length=50)
    thumbnail_sizes = models.JSONField(default=list)
    save_original = models.BooleanField(default=False)
    generate_expiring_link = models.BooleanField(default=False)
    min_expire_seconds = models.PositiveIntegerField(default=300, null=True, blank=True)
    max_expire_seconds = models.PositiveIntegerField(default=30000, null=True, blank=True)
    
    def clean(self, *args, **kwargs):
        if not self.generate_expiring_link:
            self.min_expire_seconds = None
            self.max_expire_seconds = None
            
        if (self.min_expire_seconds is not None) and (self.min_expire_seconds > self.max_expire_seconds):
            raise ValidationError("Min time can't be greater than max time")
        super().clean(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().clean(*args, **kwargs)
        
    def __str__(self):
        return self.name

class User(AbstractUser):
    tier = models.ForeignKey(UserTier, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.tier = UserTier.objects.get(name="PREMIUM")
        super().save(*args, **kwargs)



class Image(models.Model):
    def image_path(instance, filename=None):
        user_id = instance.owner.id
        dir_path = f'images/user_{user_id}'
        
        if not filename:
            return dir_path
        
        return f'{dir_path}/{filename}'
    
    def get_image_name(self):
        return os.path.basename(self.image.path)
    
    image = models.ImageField(upload_to=image_path)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Owner: {self.owner.username}; Image: {self.get_image_name()}'

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        ALLOWED_FORMATS = [
            'jpg',
            'png'
        ]
        
        self.format = self.image.name.lower().split('.')[-1]
        
        if not self.format in ALLOWED_FORMATS:
            raise ValidationError("Format not allowed")
    
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    
class Thumbnail(models.Model):
    def thumbnail_path(instance, filename):
        user_id = instance.original_image.owner.id
        return f'thumbnails/user_{user_id}/{filename}'

    thumbnail = models.ImageField(upload_to=thumbnail_path)
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='thumbnails')
    
    