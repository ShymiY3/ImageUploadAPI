from rest_framework import serializers
from . import models

class ImageSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Image
        fields = '__all__'
    
    def get_thumbnails(self, obj):
        def build_uri(path):
            request = self.context.get('request')
            return request.build_absolute_uri(path)
        
        
        return {f'{thumb.height} px' : build_uri(thumb.thumbnail.url) for thumb in obj.thumbnails.all()}