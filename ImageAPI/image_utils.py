from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PILImage
from io import BytesIO


def delete_thumbnails(instance):
    instance.thumbnails.all().delete()

def generate_thumbnail(instance, height: int, to_original = False):
    ext = instance.image.name.split('.')[-1]
    image_name = instance.get_image_name()
    thumbnail_name = image_name if to_original else f"{image_name[:image_name.rfind('.')]}_{height}px.{ext}" 
    image_path = instance.image if to_original else instance.image.path
    
    with PILImage.open(image_path) as img:
        ratio = height/img.size[1]
        width = int(img.size[0] * ratio)
        new_img = img.resize((width, height))
        output = BytesIO()
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
        
        return thumbnail_upload
            
    
    
    