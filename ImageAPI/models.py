from django.db import models
from django.core.exceptions import ValidationError
from django.core.signing import Signer
from . import image_utils
from UserAuth.models import User
import uuid
import os
import time

class Image(models.Model):
    def image_path(instance, filename=None):
        user_id = instance.owner.id
        dir_path = f'images/user_{user_id}'
        
        if not filename:
            return dir_path
        
        return f'{dir_path}/{filename}'
    
    def get_image_name(self):
        return os.path.basename(self.image.path)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to=image_path)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
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
        tier = self.owner.tier 
        if tier is not None and not tier.save_original:
            height = tier.thumbnail_sizes[0]
            self.image = image_utils.generate_thumbnail(self, height, to_original=True)
            
        super().save(*args, **kwargs)
    
    def generate_token(self, expiration_time):
        signer = Signer()
        data = f"{self.pk}:{expiration_time}:{time.time()}"
        token = signer.sign(data)
        return token
    
    
class Thumbnail(models.Model):
    def thumbnail_path(instance, filename):
        user_id = instance.original_image.owner.id
        return f'thumbnails/user_{user_id}/{filename}'

    thumbnail = models.ImageField(upload_to=thumbnail_path, editable=False)
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='thumbnails')
    height = models.IntegerField(editable=False)
    
    
    def __str__(self) -> str:
        original = str(self.original_image)
        return f'{original}; Height: {self.height}'
        