from . import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import image_utils

@receiver(pre_save, sender=models.Image)
def auto_delete_thumbnails_on_change(sender, instance, **kwargs):
    if instance.pk:
        image_utils.delete_thumbnails(instance)

@receiver(post_save, sender=models.Image)
def auto_generate_thumbnails_on_create(sender, instance, *args, **kwargs):
    if not instance.thumbnails.exists():
        image_utils.process_image(instance)
   
    
    