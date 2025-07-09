from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.ChatSessionViewSet, basename='chat-session')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'config', views.AIConfigurationViewSet, basename='ai-config')

urlpatterns = [
    path('', include(router.urls)),
]