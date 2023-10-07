from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.user_sign_in, name='sign_in'),
    path('register/', views.user_sign_up, name='sign_up'),
    path('logout/', views.user_log_out, name='log_out')
]
