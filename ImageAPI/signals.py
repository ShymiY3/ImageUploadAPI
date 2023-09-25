import os
import hashlib
from . import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings

def are_identical(image1, image2):
    hash1 = hashlib.md5(image1.read()).hexdigest()
    hash2 = hashlib.md5(image2.read()).hexdigest()
    return hash1 == hash2

def delete_files(image: models.Image):
    files = [image.image.path]
    for url in image.thumbnails.values():
        


@receiver(pre_save, sender=models.Image)
def auto_delete_images_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    
    existing_image = models.Image.objects.get(pk=instance.pk)
    if are_identical(instance.image, existing_image.image):
       return False
   
        