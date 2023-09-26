from . import models
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from urllib.parse import unquote
from PIL import Image as PILImage
from io import BytesIO


def delete_thumbnails(instance: models.Image):
    instance.thumbnails.all().delete()

def generate_thumbnail(instance: models.Image, height: int):
    ext = instance.image.name.split('.')[-1]
    image_name = instance.get_image_name()
    thumbnail_name = f"{image_name[:image_name.rfind('.')]}_{height}px.{ext}" 
    
    with PILImage.open(instance.image.path) as img:
        ratio = height/img.size[1]
        width = int(img.size[0] * ratio)
        new_img = img.resize((width, height))
        with BytesIO() as output:
            new_img.save(output, format=ext.upper())
            output.seek(0)

            thumbnail_upload = InMemoryUploadedFile(
                output, 
                'ImageField', 
                thumbnail_name, 
                f'image/{ext}',
                output.tell(), 
                None
            )
            models.Thumbnail(thumbnail=thumbnail_upload ,original_image=instance, height=height).save()
    

def process_image(instance):
    tier = instance.owner.tier
    for height in tier.thumbnail_sizes:
        generate_thumbnail(instance, height)
        
    