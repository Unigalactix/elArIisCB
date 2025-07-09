import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatSession, Message
from .services import AIService

logger = logging.getLogger('chatbot')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for session {self.session_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for session {self.session_id}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))

    async def handle_message(self, data):
        message_content = data.get('content', '')
        user = self.scope['user']
        
        if not message_content or not user.is_authenticated:
            return

        # Get chat session
        chat_session = await self.get_chat_session(user)
        if not chat_session:
            await self.send(text_data=json.dumps({
                'error': 'Chat session not found'
            }))
            return

        # Create user message
        user_message = await self.create_message(chat_session, 'user', message_content)
        
        # Send user message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': user_message.id,
                    'type': 'user',
                    'content': message_content,
                    'timestamp': user_message.created_at.isoformat()
                }
            }
        )

        # Send typing indicator
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'is_typing': True
            }
        )

        # Generate AI response
        ai_service = AIService()
        ai_response = await database_sync_to_async(ai_service.generate_response)(
            chat_session, message_content
        )

        # Create assistant message
        assistant_message = await self.create_message(chat_session, 'assistant', ai_response)

        # Send assistant message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': assistant_message.id,
                    'type': 'assistant',
                    'content': ai_response,
                    'timestamp': assistant_message.created_at.isoformat()
                }
            }
        )

        # Stop typing indicator
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'is_typing': False
            }
        )

    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        # Send typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'is_typing': is_typing,
                'user_id': self.scope['user'].id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    async def typing_indicator(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': event['is_typing'],
            'user_id': event.get('user_id')
        }))

    @database_sync_to_async
    def get_chat_session(self, user):
        try:
            return ChatSession.objects.get(
                session_id=self.session_id,
                user=user,
                is_active=True
            )
        except ChatSession.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, chat_session, message_type, content):
        return Message.objects.create(
            chat_session=chat_session,
            message_type=message_type,
            content=content
        )