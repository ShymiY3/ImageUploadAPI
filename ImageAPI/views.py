from django.shortcuts import render
from rest_framework import generics
from . import models
from . import serializers
# Create your views here.


class ImagesList(generics.ListCreateAPIView):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    
