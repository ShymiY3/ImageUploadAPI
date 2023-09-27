from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner
from . import image_utils
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
        
        if not self.save_original:
            if len(self.thumbnail_sizes) != 1:
                raise ValidationError('If save_original False, thumbnail_sizes array has to be length of 1')
        
        if not all([isinstance(x, int) for x in self.thumbnail_sizes]):
            raise (ValidationError('All values inside thumbnail_sizes array has to be integer type'))
        
        if (self.min_expire_seconds is not None) and (self.min_expire_seconds > self.max_expire_seconds):
            raise ValidationError("Min time can't be greater than max time")
        super().clean(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class User(AbstractUser):
    tier = models.ForeignKey(UserTier, on_delete=models.SET_NULL, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding and (self.is_staff or self.is_superuser):
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
        signer = TimestampSigner()
        data = f"{self.pk}:{expiration_time}"
        token = signer.sign(data)
        return token
    
    
class Thumbnail(models.Model):
    def thumbnail_path(instance, filename):
        user_id = instance.original_image.owner.id
        return f'thumbnails/user_{user_id}/{filename}'

    thumbnail = models.ImageField(upload_to=thumbnail_path)
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='thumbnails')
    height = models.IntegerField()
    
    
    def __str__(self) -> str:
        original = str(self.original_image)
        return f'{original}; Height: {self.height}'
        