from django.core.management.base import BaseCommand
from chatbot.services import AIService
import json

class Command(BaseCommand):
    help = 'Test AI service connection (Azure OpenAI or OpenAI)'

    def handle(self, *args, **options):
        self.stdout.write('Testing AI service connection...\n')
        
        ai_service = AIService()
        result = ai_service.test_connection()
        
        self.stdout.write(f"Status: {result['status']}")
        self.stdout.write(f"Service: {result['service']}")
        
        if result['status'] == 'success':
            self.stdout.write(self.style.SUCCESS('✓ AI service connection successful!'))
            if 'model' in result:
                self.stdout.write(f"Model: {result['model']}")
            if 'endpoint' in result:
                self.stdout.write(f"Endpoint: {result['endpoint']}")
        elif result['status'] == 'fallback':
            self.stdout.write(self.style.WARNING('⚠ Using fallback responses'))
            self.stdout.write(f"Message: {result['message']}")
        else:
            self.stdout.write(self.style.ERROR('✗ AI service connection failed'))
            self.stdout.write(f"Error: {result['error']}")
            
        self.stdout.write('\nConfiguration check:')
        self.stdout.write(f"Azure OpenAI configured: {'Yes' if ai_service.azure_openai_api_key else 'No'}")
        self.stdout.write(f"Standard OpenAI configured: {'Yes' if ai_service.openai_api_key else 'No'}")