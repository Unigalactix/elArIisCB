import openai
import logging
from django.conf import settings
from .models import AIConfiguration, ChatSession, Message

logger = logging.getLogger('chatbot')

class AIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.azure_openai_api_key = settings.AZURE_OPENAI_API_KEY
        self.azure_openai_endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.azure_openai_api_version = settings.AZURE_OPENAI_API_VERSION
        self.azure_openai_deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        
        # Configure OpenAI client based on available credentials
        if self.azure_openai_api_key and self.azure_openai_endpoint:
            # Configure for Azure OpenAI
            openai.api_type = "azure"
            openai.api_key = self.azure_openai_api_key
            openai.api_base = self.azure_openai_endpoint
            openai.api_version = self.azure_openai_api_version
            self.use_azure = True
            logger.info("Configured for Azure OpenAI")
        elif self.openai_api_key:
            # Configure for standard OpenAI
            openai.api_key = self.openai_api_key
            openai.api_type = "open_ai"
            self.use_azure = False
            logger.info("Configured for standard OpenAI")
        else:
            self.use_azure = False
            logger.info("No OpenAI API keys configured, using fallback responses")

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
            if self.azure_openai_api_key or self.openai_api_key:
                response = self._generate_openai_response(messages, config)
            else:
                response = self._generate_fallback_response(user_message, chat_session.user)

            logger.info(f"Generated response for user {chat_session.user.username}")
            return response

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._generate_error_response()

    def _generate_openai_response(self, messages, config):
        """Generate response using OpenAI API (Azure or Standard)"""
        try:
            if self.use_azure:
                # Azure OpenAI API call
                response = openai.ChatCompletion.create(
                    engine=self.azure_openai_deployment_name,  # Use engine for Azure
                    messages=messages,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens
                )
            else:
                # Standard OpenAI API call
                response = openai.ChatCompletion.create(
                    model=config.model_name,
                    messages=messages,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens
                )
            
            return response.choices[0].message.content
            
        except openai.error.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            return "I'm experiencing high demand right now. Please try again in a moment."
        except openai.error.InvalidRequestError as e:
            logger.error(f"OpenAI API invalid request: {str(e)}")
            return "I'm having trouble processing your request. Please try rephrasing your question."
        except openai.error.AuthenticationError:
            logger.error("OpenAI API authentication failed")
            return self._generate_fallback_response("", None)
        except openai.error.APIConnectionError:
            logger.error("OpenAI API connection error")
            return "I'm having trouble connecting to my AI service. Please try again later."
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_fallback_response("", None)

    def _generate_fallback_response(self, user_message: str, user) -> str:
        """Generate fallback response when OpenAI is not available"""
        user_message_lower = user_message.lower()
        
        # Azure AI Foundry specific responses
        if any(keyword in user_message_lower for keyword in ['azure', 'ai foundry', 'gpt-4', 'openai']):
            return "I'm powered by Azure AI Foundry's GPT-4 model to provide you with intelligent assistance. How can I help you with your workplace needs today?"
        
        # HR-related responses
        elif any(keyword in user_message_lower for keyword in ['hr', 'human resources', 'payroll', 'benefits', 'leave', 'vacation']):
            return "I can help you with HR-related questions! For specific HR matters like payroll, benefits, or leave requests, I recommend visiting the HR Management portal or contacting your HR representative directly. What specific HR topic would you like assistance with?"
        
        # IT-related responses
        elif any(keyword in user_message_lower for keyword in ['it', 'technical', 'computer', 'software', 'password', 'system']):
            return "For technical support and IT-related issues, I can guide you through common solutions or help you submit a support ticket. What technical issue are you experiencing?"
        
        # Employee portal responses
        elif any(keyword in user_message_lower for keyword in ['employee', 'portal', 'profile', 'directory']):
            return "You can access your employee information, update your profile, and view the company directory through the Employee Portal. What specific information are you looking for?"
        
        # Greeting responses
        elif any(keyword in user_message_lower for keyword in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            name = user.first_name if user and user.first_name else "there"
            return f"Hello {name}! I'm your AI assistant powered by Azure AI Foundry. I'm here to help with HR questions, IT support, employee services, and general workplace information. What can I assist you with today?"
        
        # General help
        elif any(keyword in user_message_lower for keyword in ['help', 'support', 'assistance']):
            return "I'm here to help! I can assist you with:\n\n• HR-related questions and processes\n• IT support and technical issues\n• Employee portal navigation\n• General workplace information\n• Policy and procedure questions\n\nWhat would you like to know about?"
        
        # Default response
        else:
            return "I understand you're looking for assistance. Could you please provide more details about what you need help with? I can help with HR matters, IT support, employee services, and general workplace questions. I'm powered by Azure AI Foundry to provide you with the best possible assistance."

    def _generate_error_response(self) -> str:
        """Generate error response when AI service fails"""
        return "I'm sorry, but I'm having trouble processing your request right now. Please try again in a moment, or contact IT support if the issue persists."

    def _get_default_config(self) -> AIConfiguration:
        """Get or create default AI configuration"""
        # Determine default model based on configuration
        default_model = self.azure_openai_deployment_name if self.use_azure else 'gpt-3.5-turbo'
        
        config, created = AIConfiguration.objects.get_or_create(
            name='default',
            defaults={
                'model_name': default_model,
                'temperature': 0.7,
                'max_tokens': 1000,
                'system_prompt': """You are a helpful AI assistant for the Elariis Portal, a corporate employee management system, powered by Azure AI Foundry's GPT-4 model.
                
Your role is to assist employees with:
- HR-related questions (benefits, payroll, leave requests, policies)
- IT support (technical issues, password resets, software problems)
- Employee portal navigation and features
- General workplace information and procedures
- Company policies and guidelines

Key guidelines:
1. Always be professional, helpful, and concise
2. Provide accurate information based on common workplace practices
3. If you cannot answer a specific question, direct users to the appropriate department
4. Maintain confidentiality and don't ask for sensitive personal information
5. Be proactive in offering related help or suggestions
6. Use a friendly but professional tone
7. Remember that you're representing the company

Always maintain a professional tone while being friendly and approachable. You're an integral part of the employee experience at Elariis."""
            }
        )
        return config

    def test_connection(self) -> dict:
        """Test the AI service connection"""
        try:
            test_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a connection test."}
            ]
            
            if self.use_azure:
                response = openai.ChatCompletion.create(
                    engine=self.azure_openai_deployment_name,
                    messages=test_messages,
                    temperature=0.7,
                    max_tokens=50
                )
                return {
                    'status': 'success',
                    'service': 'Azure OpenAI',
                    'model': self.azure_openai_deployment_name,
                    'endpoint': self.azure_openai_endpoint
                }
            elif self.openai_api_key:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=test_messages,
                    temperature=0.7,
                    max_tokens=50
                )
                return {
                    'status': 'success',
                    'service': 'OpenAI',
                    'model': 'gpt-3.5-turbo'
                }
            else:
                return {
                    'status': 'fallback',
                    'service': 'Fallback responses',
                    'message': 'No API keys configured'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'service': 'Azure OpenAI' if self.use_azure else 'OpenAI',
                'error': str(e)
            }