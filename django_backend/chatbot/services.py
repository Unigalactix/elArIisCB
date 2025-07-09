import openai
import logging
from django.conf import settings
from .models import AIConfiguration, ChatSession, Message

logger = logging.getLogger('chatbot')

class AIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    def generate_response(self, chat_session: ChatSession, user_message: str) -> str:
        """Generate AI response based on chat history and user message"""
        try:
            # Get AI configuration
            config = AIConfiguration.objects.filter(is_active=True).first()
            if not config:
                config = self._get_default_config()

            # Get recent chat history
            recent_messages = chat_session.messages.order_by('-created_at')[:10]
            
            # Build conversation context
            messages = [{"role": "system", "content": config.system_prompt}]
            
            for msg in reversed(recent_messages):
                if msg.message_type == 'user':
                    messages.append({"role": "user", "content": msg.content})
                elif msg.message_type == 'assistant':
                    messages.append({"role": "assistant", "content": msg.content})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Generate response
            if self.openai_api_key:
                response = self._generate_openai_response(messages, config)
            else:
                response = self._generate_fallback_response(user_message, chat_session.user)

            logger.info(f"Generated response for user {chat_session.user.username}")
            return response

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._generate_error_response()

    def _generate_openai_response(self, messages, config):
        """Generate response using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=config.model_name,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_fallback_response("", None)

    def _generate_fallback_response(self, user_message: str, user) -> str:
        """Generate fallback response when OpenAI is not available"""
        user_message_lower = user_message.lower()
        
        # HR-related responses
        if any(keyword in user_message_lower for keyword in ['hr', 'human resources', 'payroll', 'benefits', 'leave', 'vacation']):
            return "I can help you with HR-related questions! For specific HR matters like payroll, benefits, or leave requests, I recommend visiting the HR Management portal or contacting your HR representative directly."
        
        # IT-related responses
        elif any(keyword in user_message_lower for keyword in ['it', 'technical', 'computer', 'software', 'password', 'system']):
            return "For technical support and IT-related issues, please visit the IT Help Desk portal or submit a support ticket. Our IT team will assist you with any technical problems."
        
        # Employee portal responses
        elif any(keyword in user_message_lower for keyword in ['employee', 'portal', 'profile', 'directory']):
            return "You can access your employee information, update your profile, and view the company directory through the Employee Portal. Is there something specific you'd like to know about?"
        
        # Greeting responses
        elif any(keyword in user_message_lower for keyword in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            name = user.first_name if user and user.first_name else "there"
            return f"Hello {name}! I'm your AI assistant for the Elariis Portal. How can I help you today? I can assist with questions about HR, IT support, employee services, and more."
        
        # General help
        elif any(keyword in user_message_lower for keyword in ['help', 'support', 'assistance']):
            return "I'm here to help! I can assist you with:\n\n• HR-related questions and processes\n• IT support and technical issues\n• Employee portal navigation\n• General workplace information\n\nWhat would you like to know about?"
        
        # Default response
        else:
            return "I understand you're looking for assistance. Could you please provide more details about what you need help with? I can help with HR matters, IT support, employee services, and general workplace questions."

    def _generate_error_response(self) -> str:
        """Generate error response when AI service fails"""
        return "I'm sorry, but I'm having trouble processing your request right now. Please try again in a moment, or contact IT support if the issue persists."

    def _get_default_config(self) -> AIConfiguration:
        """Get or create default AI configuration"""
        config, created = AIConfiguration.objects.get_or_create(
            name='default',
            defaults={
                'model_name': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000,
                'system_prompt': """You are a helpful AI assistant for the Elariis Portal, a corporate employee management system. 
                
Your role is to assist employees with:
- HR-related questions (benefits, payroll, leave requests, policies)
- IT support (technical issues, password resets, software problems)
- Employee portal navigation and features
- General workplace information and procedures

Always be professional, helpful, and concise. If you cannot answer a specific question, direct users to the appropriate department or portal section. Remember that you're representing the company, so maintain a professional tone while being friendly and approachable."""
            }
        )
        return config