from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import RedirectView


router = DefaultRouter()
router.register('images', views.ImageViewSet, basename='images')

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    path('token/obtain', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('shared/', RedirectView.as_view(pattern_name='api-root', permanent=False), name='shared'),
    path('shared/<str:token>', views.access_expiring_link, name='access-expiring-link')
]
