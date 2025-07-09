# Azure OpenAI Integration Setup Guide

This guide will help you integrate Azure OpenAI (GPT-4) from Azure AI Foundry with your Django chatbot backend.

## 🚀 Prerequisites

1. **Azure Subscription**: Active Azure subscription
2. **Azure OpenAI Resource**: Created in Azure AI Foundry
3. **GPT-4 Model Deployment**: Deployed GPT-4 model in your Azure OpenAI resource

## 📋 Step-by-Step Setup

### 1. Create Azure OpenAI Resource

1. Go to [Azure AI Foundry](https://ai.azure.com/)
2. Create a new Azure OpenAI resource
3. Choose your subscription, resource group, and region
4. Wait for deployment to complete

### 2. Deploy GPT-4 Model

1. In Azure AI Foundry, navigate to your OpenAI resource
2. Go to "Model deployments"
3. Click "Create new deployment"
4. Select GPT-4 model
5. Choose deployment name (e.g., "gpt-4")
6. Configure capacity and settings
7. Deploy the model

### 3. Get API Credentials

1. In your Azure OpenAI resource, go to "Keys and Endpoint"
2. Copy the following information:
   - **API Key**: One of the two keys provided
   - **Endpoint**: The endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
   - **API Version**: Current version (e.g., `2024-02-15-preview`)
   - **Deployment Name**: The name you gave your GPT-4 deployment

### 4. Configure Django Backend

1. **Update Environment Variables**:
   ```bash
   # In your .env file
   AZURE_OPENAI_API_KEY=your-azure-openai-api-key
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   ```

2. **Install Dependencies**:
   ```bash
   pip install azure-identity==1.15.0
   ```

3. **Test Connection**:
   ```bash
   python manage.py test_ai_connection
   ```

### 5. Verify Integration

1. **Start Django Server**:
   ```bash
   python manage.py runserver
   ```

2. **Test API Endpoint**:
   ```bash
   curl -H "Authorization: Token your-token" \
        http://localhost:8000/api/v1/chat/test-connection/
   ```

3. **Expected Response**:
   ```json
   {
     "status": "success",
     "service": "Azure OpenAI",
     "model": "gpt-4",
     "endpoint": "https://your-resource.openai.azure.com/"
   }
   ```

## 🔧 Configuration Options

### Model Configuration

Update AI configuration in Django admin:

1. Go to `http://localhost:8000/admin/`
2. Navigate to "Chatbot" → "AI Configurations"
3. Update the default configuration:
   - **Model Name**: `gpt-4` (your deployment name)
   - **Temperature**: `0.7` (creativity level)
   - **Max Tokens**: `1000` (response length)
   - **System Prompt**: Customize for your use case

### Advanced Settings

```python
# In settings.py, you can also configure:
AZURE_OPENAI_API_VERSION = '2024-02-15-preview'  # Latest API version
AZURE_OPENAI_DEPLOYMENT_NAME = 'gpt-4'           # Your deployment name
```

## 🛡️ Security Best Practices

### 1. Environment Variables
- Never commit API keys to version control
- Use environment variables for all sensitive data
- Rotate API keys regularly

### 2. Access Control
- Limit API key permissions in Azure
- Use managed identities when possible
- Monitor API usage and costs

### 3. Rate Limiting
- Configure appropriate rate limits
- Implement retry logic with exponential backoff
- Monitor quota usage

## 📊 Monitoring & Troubleshooting

### Common Issues

1. **Authentication Error**:
   ```
   Error: OpenAI API authentication failed
   ```
   - Verify API key is correct
   - Check if key has expired
   - Ensure proper permissions

2. **Endpoint Error**:
   ```
   Error: OpenAI API connection error
   ```
   - Verify endpoint URL format
   - Check network connectivity
   - Ensure resource is deployed

3. **Model Not Found**:
   ```
   Error: The model 'gpt-4' does not exist
   ```
   - Verify deployment name matches configuration
   - Check if model is properly deployed
   - Ensure model is in the same region

### Testing Commands

```bash
# Test AI connection
python manage.py test_ai_connection

# Check Django logs
tail -f chatbot.log

# Test with curl
curl -X POST http://localhost:8000/api/v1/chat/sessions/1/send_message/ \
     -H "Authorization: Token your-token" \
     -H "Content-Type: application/json" \
     -d '{"content": "Hello, test message"}'
```

### Monitoring Dashboard

Monitor your Azure OpenAI usage:
1. Go to Azure Portal
2. Navigate to your OpenAI resource
3. Check "Metrics" for usage statistics
4. Set up alerts for quota limits

## 💰 Cost Management

### Pricing Considerations
- GPT-4 is more expensive than GPT-3.5
- Monitor token usage carefully
- Set up billing alerts
- Consider using GPT-3.5 for simple queries

### Optimization Tips
1. **Limit Max Tokens**: Reduce `max_tokens` for shorter responses
2. **Optimize Prompts**: Use concise system prompts
3. **Cache Responses**: Implement caching for common queries
4. **Fallback Strategy**: Use cheaper models for simple queries

## 🔄 Fallback Strategy

The system automatically falls back to:
1. **Standard OpenAI**: If Azure OpenAI fails
2. **Rule-based Responses**: If no API keys are configured
3. **Error Messages**: If all services fail

## 📈 Performance Optimization

### Response Time
- Azure OpenAI typically has lower latency than standard OpenAI
- Choose regions close to your users
- Implement async processing for better UX

### Scalability
- Use connection pooling
- Implement request queuing
- Monitor concurrent request limits

## 🧪 Testing

### Unit Tests
```python
# Test AI service
from chatbot.services import AIService

def test_azure_openai_integration():
    ai_service = AIService()
    result = ai_service.test_connection()
    assert result['status'] == 'success'
    assert result['service'] == 'Azure OpenAI'
```

### Integration Tests
```bash
# Run full test suite
python manage.py test chatbot.tests.test_ai_service
```

## 📚 Additional Resources

- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure AI Foundry](https://ai.azure.com/)
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Azure OpenAI service health
3. Check Django logs for detailed error messages
4. Test connection using the management command
5. Verify all environment variables are set correctly

---

**Note**: This integration supports both Azure OpenAI and standard OpenAI APIs, with automatic fallback to rule-based responses if neither is available.