from rest_framework import serializers
from . import models


class ImageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    thumbnails = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = models.Image
        fields = '__all__'
    
    def get_thumbnails(self, obj):
        def build_uri(path):
            request = self.context.get('request')
            return request.build_absolute_uri(path)
    
        return {f'{thumb.height} px' : build_uri(thumb.thumbnail.url) for thumb in obj.thumbnails.all()}
    
class ImageListSerializer(ImageSerializer, serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='images-detail',
        lookup_field = 'pk'
    )
    
    filename = serializers.ReadOnlyField(source = 'get_image_name')
    
    class Meta(ImageSerializer.Meta):
        fields = (
            'owner',
            'url',
            'filename',
        )
    
        
class ImageDetailSerializer(ImageSerializer):
    class Meta(ImageSerializer.Meta):
        fields = (
            'id',
            'owner',
            'image',
            'thumbnails',
            'created_at',
            'modified_at',
        )
        read_only_fields = list(fields)
        
        
class ImageCreateUpdateSerializer(ImageSerializer):
    class Meta(ImageDetailSerializer.Meta):
        read_only_fields = ImageDetailSerializer.Meta.read_only_fields
        read_only_fields.remove('image')
        
from rest_framework import serializers

class ExpiringLinkSerializer(serializers.Serializer):
    expiration_time = serializers.IntegerField()

    def validate_expiration_time(self, value):
        tier = self.context.get('request').user.tier

        min_time = tier.min_expire_seconds
        max_time = tier.max_expire_seconds
        
        if not min_time <= value <= max_time:
            raise serializers.ValidationError(f'Expiration time must be between {min_time} - {max_time}')
        
        return value