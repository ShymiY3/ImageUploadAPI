from rest_framework.response import Response
from rest_framework import viewsets, status, permissions as RestPermissions
from rest_framework.decorators import action, api_view
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.urls import reverse
from django.http import HttpResponse
from . import (
    models,
    serializers,
    permissions
)
import time

class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ImageSerializer
    permission_classes = [permissions.IsOwnerOrStaf, RestPermissions.IsAuthenticatedOrReadOnly]
    
    action_serializers = {
        'list': serializers.ImageListSerializer,
        'retrieve' : serializers.ImageDetailSerializer,
        'create' : serializers.ImageCreateUpdateSerializer,
        'update' : serializers.ImageCreateUpdateSerializer,
        'expiring_link' : serializers.ExpiringLinkSerializer,
    }
    
    
    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            return self.action_serializers.get(self.action, self.serializer_class)
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user 
        
        if user.is_anonymous:
            return models.Image.objects.none()
        
        if user.is_staff:
            qs = models.Image.objects.all().order_by('-modified_at')
            username = self.request.query_params.get('username')
            if username is not None:
                qs = qs.filter(owner__username__iexact=username)
            return qs
            
        return models.Image.objects.filter(owner=user).order_by('-modified_at')
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    @action(detail=True, methods=['POST'])
    def expiring_link(self, request, *args, **kwargs):
        image = self.get_object()
        serializer = serializers.ExpiringLinkSerializer(data=request.data, context={'request' : self.request})
        
        if serializer.is_valid():
            expiration_time = serializer.validated_data['expiration_time']
            token = image.generate_token(expiration_time)
            url = reverse('shared') + token
            link = request.build_absolute_uri(url)
            return Response({'url' : link}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['GET'], url_name='show-image')
    def show_image(self, request , *args, **kwargs):
        image = self.get_object()
        ext = image.image.name.rsplit('.', 1)[-1]
        return HttpResponse(image.image.read(), content_type=f'image/{ext}') 

    @action(detail=True, methods=['GET'], url_name='show-thumbnail')
    def show_thumbnail(self, request , *args, **kwargs):
        image = self.get_object()
        if not image.thumbnails.exists():
            return Response({'detail': "Image doesn't have thumbnails"}, status=status.HTTP_404_NOT_FOUND)
        
        thumbnail_height = request.query_params.get('height', None)
        if thumbnail_height is None:
            thumbnail = image.thumbnails.first()
        else:
            thumbnail = image.thumbnails.filter(height=thumbnail_height).first()

        if not thumbnail:
            return Response({'detail': "Thumbnail with this height doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        
        ext = thumbnail.thumbnail.name.rsplit('.', 1)[-1]
        return HttpResponse(thumbnail.thumbnail.read(), content_type=f'image/{ext}') 

@api_view(['GET'])
def access_expiring_link(request, token):
    signer = Signer()
    
    try:
        data = signer.unsign(token)
        image_id, expiration_time, timestamp = data.rsplit(':', 2)
        if time.time() - float(timestamp) > int(expiration_time):
            raise SignatureExpired()
        image = models.Image.objects.get(id=image_id)
        ext = image.image.name.rsplit('.', 1)[-1]
        return HttpResponse(image.image.read(), content_type=f'image/{ext}') 
    except SignatureExpired:
        return Response({'detail': 'The link has expired.'}, status=status.HTTP_400_BAD_REQUEST)
    except BadSignature:
        return Response({'detail': 'The link does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    except models.Image.DoesNotExist:
        return Response({'detail': 'The image has been deleted.'}, status=status.HTTP_404_NOT_FOUND)
    
