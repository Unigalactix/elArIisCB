from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatSession, Message, AIConfiguration, ChatAnalytics
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer,
    MessageSerializer, AIConfigurationSerializer, ChatAnalyticsSerializer
)
from .services import AIService
import uuid

class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            session_id=uuid.uuid4()
        )

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat_session = self.get_object()
        content = request.data.get('content', '')
        
        if not content:
            return Response({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user message
        user_message = Message.objects.create(
            chat_session=chat_session,
            message_type='user',
            content=content
        )

        # Get AI response
        ai_service = AIService()
        ai_response = ai_service.generate_response(chat_session, content)

        # Create assistant message
        assistant_message = Message.objects.create(
            chat_session=chat_session,
            message_type='assistant',
            content=ai_response
        )

        # Update chat session
        chat_session.save()

        return Response({
            'user_message': MessageSerializer(user_message).data,
            'assistant_message': MessageSerializer(assistant_message).data
        })

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat_session = self.get_object()
        messages = chat_session.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        chat_session = self.get_object()
        chat_session.is_active = False
        chat_session.save()
        return Response({'message': 'Chat session ended'})

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(chat_session__user=self.request.user)

class AIConfigurationViewSet(viewsets.ModelViewSet):
    queryset = AIConfiguration.objects.all()
    serializer_class = AIConfigurationSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False)
    def active_config(self, request):
        config = AIConfiguration.objects.filter(is_active=True).first()
        if config:
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        return Response({'error': 'No active configuration found'}, status=status.HTTP_404_NOT_FOUND)