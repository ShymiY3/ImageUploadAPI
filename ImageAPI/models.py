from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from PIL import Image as PILImage
from io import BytesIO
from urllib.parse import quote, unquote
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
    def image_path(instance, filename):
        user_id = instance.owner.id
    
        return f'images/user_{user_id}/{filename}'
    
    def get_image_name(self):
        return self.image.name.split('/')[-1]
    
    image = models.ImageField(upload_to=image_path)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnails = models.JSONField(default=dict, null=True, blank=True)
    
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
        self.process_image()
        super().save(*args, **kwargs)
    
    
    def process_image(self):
        tier = self.owner.tier
        
        for height in tier.thumbnail_sizes:
            thumbnail = self.generate_thumbnail(height)
            self.append_thumbnail(height, thumbnail)

    
    def generate_thumbnail(self, height):
        img = PILImage.open(self.image)
        
        ratio = height/img.size[1]
        width = int(img.size[0] * ratio)
        img = img.resize((width, height))
        
        image_dir = os.path.dirname(self.image.path)
        image_name = self.get_image_name()
        thumbnail_name = f"{image_name[:image_name.rfind('.')]}_{height}px.{self.format}" 
        thumbnail_path =  os.path.join(image_dir, thumbnail_name)
        print(thumbnail_path)
        img.save(thumbnail_path, format=self.format.upper())

        return thumbnail_name
    
    def append_thumbnail(self, height, thumbnail):
        thumbnail = quote(thumbnail)
        thumbnail_url = self.image_path(thumbnail)
        self.thumbnails[f'{height}px'] = thumbnail_url
    
    