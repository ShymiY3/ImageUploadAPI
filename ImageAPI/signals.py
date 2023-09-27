from . import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . import image_utils

@receiver(pre_save, sender=models.Image)
def auto_delete_thumbnails_on_change(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(id=instance.id)
        if old_instance.image != instance.image:
            image_utils.delete_thumbnails(instance)
    except sender.DoesNotExist:
        pass
        
@receiver(post_save, sender=models.Image)
def auto_generate_thumbnails_on_create(sender, instance, *args, **kwargs):
    if not instance.thumbnails.exists():
        tier = instance.owner.tier
    
        if tier is None or not tier.save_original:
            return
    
        for height in tier.thumbnail_sizes:
            thumbnail_upload = image_utils.generate_thumbnail(instance, height)
            models.Thumbnail(thumbnail=thumbnail_upload ,original_image=instance, height=height).save()
        
    
    