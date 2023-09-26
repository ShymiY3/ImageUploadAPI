from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('', views.ImagesList.as_view(), name='image-list')
    
]
