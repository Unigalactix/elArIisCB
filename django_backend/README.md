# Elariis Portal AI Assistant Backend

A comprehensive Django-based backend system for the AI Assistant chatbot integrated with the Elariis Portal. This system provides real-time chat capabilities, user management, AI integration, and analytics for enterprise employee portals.

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Technical Stack](#technical-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [WebSocket Integration](#websocket-integration)
- [Database Schema](#database-schema)
- [AI Integration](#ai-integration)
- [Security Features](#security-features)
- [Background Tasks](#background-tasks)
- [Monitoring & Analytics](#monitoring--analytics)
- [Frontend Integration](#frontend-integration)
- [Deployment](#deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

### Core Functionality
- **Real-time Chat**: WebSocket-based instant messaging with typing indicators
- **User Authentication**: Token-based authentication with extended user profiles
- **Message Persistence**: Complete chat history storage with PostgreSQL
- **AI Integration**: Flexible AI service integration with OpenAI API support
- **Session Management**: Multi-session support per user with session persistence
- **Analytics**: Comprehensive chat analytics and reporting
- **Admin Interface**: Django admin for managing users, chats, and configurations

### Advanced Features
- **Background Tasks**: Celery integration for async processing
- **Caching**: Redis-based caching and session storage
- **Rate Limiting**: Built-in protection against abuse
- **File Uploads**: Support for avatar uploads and file attachments
- **CORS Support**: Configured for React frontend integration
- **Logging**: Comprehensive logging system with file and console output
- **Docker Support**: Complete containerization setup
- **Scalability**: Designed for horizontal scaling

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Django Backend │    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│    Database     │
│  - Chat UI      │    │  - REST API     │    │                 │
│  - WebSocket    │    │  - WebSocket    │    │  - Users        │
│  - Auth         │    │  - Auth         │    │  - Messages     │
└─────────────────┘    └─────────────────┘    │  - Sessions     │
                                              └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │      Redis      │    │     Celery      │
                       │                 │    │                 │
                       │  - Caching      │◄──►│  - Background   │
                       │  - Sessions     │    │    Tasks        │
                       │  - WebSocket    │    │  - Analytics    │
                       └─────────────────┘    └─────────────────┘
```

### Application Structure
```
django_backend/
├── elariis_backend/          # Main Django project
│   ├── settings.py          # Configuration
│   ├── urls.py              # URL routing
│   ├── asgi.py              # ASGI configuration
│   └── wsgi.py              # WSGI configuration
├── accounts/                # User management app
│   ├── models.py            # User model extensions
│   ├── views.py             # Authentication views
│   ├── serializers.py       # API serializers
│   └── admin.py             # Admin interface
├── chatbot/                 # Core chatbot functionality
│   ├── models.py            # Chat models
│   ├── views.py             # API views
│   ├── consumers.py         # WebSocket consumers
│   ├── services.py          # AI service integration
│   ├── tasks.py             # Background tasks
│   └── admin.py             # Admin interface
└── requirements.txt         # Python dependencies
```

## Technical Stack

### Backend Framework
- **Django 4.2.7**: Web framework with ORM and admin interface
- **Django REST Framework 3.14.0**: API development toolkit
- **Django Channels 4.0.0**: WebSocket and async support
- **Daphne 4.0.0**: ASGI server for WebSocket handling

### Database & Caching
- **PostgreSQL 15+**: Primary database for data persistence
- **Redis 7+**: Caching, session storage, and WebSocket channel layer
- **psycopg2-binary 2.9.7**: PostgreSQL adapter for Python

### AI & External Services
- **OpenAI 1.3.5**: AI service integration
- **Celery 5.3.4**: Distributed task queue
- **channels-redis 4.1.0**: Redis channel layer for WebSockets

### Development & Deployment
- **Docker & Docker Compose**: Containerization
- **Gunicorn 21.2.0**: WSGI server for production
- **WhiteNoise 6.6.0**: Static file serving
- **python-decouple 3.8**: Environment variable management

## Installation

### Prerequisites

Ensure you have the following installed:
- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis 7 or higher
- Git
- (Optional) Docker and Docker Compose

### Local Development Setup

1. **Clone the Repository**
```bash
git clone <repository-url>
cd django_backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=elariis_chatbot
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379

# AI Configuration (Optional)
OPENAI_API_KEY=your-openai-api-key
```

5. **Database Setup**
```bash
# Create database (PostgreSQL)
createdb elariis_chatbot

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Start Services**
```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A elariis_backend worker -l info

# Terminal 3: Celery beat (optional, for scheduled tasks)
celery -A elariis_backend beat -l info
```

### Docker Setup

1. **Start All Services**
```bash
docker-compose up -d
```

2. **Run Initial Setup**
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

3. **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key | - | Yes |
| `DEBUG` | Debug mode | `True` | No |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | `localhost,127.0.0.1` | No |
| `DB_NAME` | Database name | `elariis_chatbot` | Yes |
| `DB_USER` | Database user | `postgres` | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `DB_HOST` | Database host | `localhost` | No |
| `DB_PORT` | Database port | `5432` | No |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | No |

### Django Settings

Key settings in `settings.py`:

```python
# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
]

# WebSocket Configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
```

### AI Configuration

Configure AI settings through Django admin:

1. Access admin at `http://localhost:8000/admin/`
2. Navigate to "Chatbot" → "AI Configurations"
3. Create/modify configuration:
   - **Name**: Configuration identifier
   - **Model Name**: AI model (e.g., "gpt-3.5-turbo")
   - **Temperature**: Response randomness (0.0-1.0)
   - **Max Tokens**: Maximum response length
   - **System Prompt**: AI behavior instructions
   - **Is Active**: Enable/disable configuration

## API Documentation

### Authentication Endpoints

#### POST `/api/v1/auth/login/`
User login with credentials.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "employee_id": "EMP001",
    "department": "IT",
    "position": "Developer",
    "is_hr": false,
    "is_it_support": true
  }
}
```

#### POST `/api/v1/auth/register/`
User registration.

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "employee_id": "EMP002",
  "department": "HR",
  "position": "HR Manager"
}
```

#### POST `/api/v1/auth/logout/`
User logout (requires authentication).

#### GET `/api/v1/auth/profile/`
Get current user profile (requires authentication).

### Chat Endpoints

#### GET `/api/v1/chat/sessions/`
List user's chat sessions.

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "IT Support Chat",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:45:00Z",
      "message_count": 8,
      "last_message": {
        "id": 16,
        "message_type": "assistant",
        "content": "I've created a support ticket for you...",
        "created_at": "2024-01-15T11:45:00Z"
      }
    }
  ]
}
```

#### POST `/api/v1/chat/sessions/`
Create new chat session.

**Request:**
```json
{
  "title": "New Chat Session"
}
```

#### GET `/api/v1/chat/sessions/{id}/`
Get specific chat session with messages.

#### POST `/api/v1/chat/sessions/{id}/send_message/`
Send message to chat session.

**Request:**
```json
{
  "content": "Hello, I need help with my password reset"
}
```

**Response:**
```json
{
  "user_message": {
    "id": 17,
    "message_type": "user",
    "content": "Hello, I need help with my password reset",
    "created_at": "2024-01-15T12:00:00Z"
  },
  "assistant_message": {
    "id": 18,
    "message_type": "assistant",
    "content": "I can help you with password reset. Please visit...",
    "created_at": "2024-01-15T12:00:01Z"
  }
}
```

#### GET `/api/v1/chat/sessions/{id}/messages/`
Get messages for specific session.

#### POST `/api/v1/chat/sessions/{id}/end_session/`
End chat session.

### Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": {
    "field": ["Specific field error"]
  }
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## WebSocket Integration

### Connection

Connect to WebSocket endpoint:
```
ws://localhost:8000/ws/chat/{session_id}/
```

### Authentication

WebSocket connections use Django session authentication. Ensure user is logged in before connecting.

### Message Types

#### Send Message
```json
{
  "type": "message",
  "content": "Hello, AI assistant!"
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "is_typing": true
}
```

### Received Messages

#### Chat Message
```json
{
  "type": "message",
  "message": {
    "id": 123,
    "type": "assistant",
    "content": "Hello! How can I help you?",
    "timestamp": "2024-01-15T12:00:00Z"
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "is_typing": true,
  "user_id": 1
}
```

#### Error Message
```json
{
  "error": "Failed to process message"
}
```

### JavaScript Example

```javascript
class ChatWebSocket {
  constructor(sessionId, token) {
    this.sessionId = sessionId;
    this.token = token;
    this.ws = null;
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws/chat/${this.sessionId}/`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Implement reconnection logic
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  sendMessage(content) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'message',
        content: content
      }));
    }
  }

  sendTyping(isTyping) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'message':
        this.displayMessage(data.message);
        break;
      case 'typing':
        this.showTypingIndicator(data.is_typing);
        break;
      case 'error':
        this.showError(data.error);
        break;
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const chat = new ChatWebSocket('session-uuid', 'auth-token');
chat.connect();
```

## Database Schema

### User Model (Extended)
```sql
CREATE TABLE accounts_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    employee_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20),
    avatar VARCHAR(100),
    is_hr BOOLEAN DEFAULT FALSE,
    is_it_support BOOLEAN DEFAULT FALSE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Chat Session Model
```sql
CREATE TABLE chatbot_chatsession (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES accounts_user(id),
    session_id UUID UNIQUE NOT NULL,
    title VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_chatsession_user ON chatbot_chatsession(user_id);
CREATE INDEX idx_chatsession_active ON chatbot_chatsession(is_active);
```

### Message Model
```sql
CREATE TABLE chatbot_message (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER REFERENCES chatbot_chatsession(id),
    message_type VARCHAR(10) CHECK (message_type IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_message_session ON chatbot_message(chat_session_id);
CREATE INDEX idx_message_type ON chatbot_message(message_type);
CREATE INDEX idx_message_created ON chatbot_message(created_at);
```

### AI Configuration Model
```sql
CREATE TABLE chatbot_aiconfiguration (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    temperature DECIMAL(3,2) DEFAULT 0.70,
    max_tokens INTEGER DEFAULT 1000,
    system_prompt TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Analytics Model
```sql
CREATE TABLE chatbot_chatanalytics (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER UNIQUE REFERENCES chatbot_chatsession(id),
    total_messages INTEGER DEFAULT 0,
    user_messages INTEGER DEFAULT 0,
    assistant_messages INTEGER DEFAULT 0,
    average_response_time DECIMAL(10,2) DEFAULT 0.00,
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## AI Integration

### Service Architecture

The AI service is designed with a flexible architecture supporting multiple AI providers:

```python
class AIService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        
    def generate_response(self, chat_session, user_message):
        """Main entry point for AI response generation"""
        if self.openai_api_key:
            return self._generate_openai_response(messages, config)
        else:
            return self._generate_fallback_response(user_message, user)
```

### OpenAI Integration

When OpenAI API key is configured:

```python
def _generate_openai_response(self, messages, config):
    response = openai.ChatCompletion.create(
        model=config.model_name,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens
    )
    return response.choices[0].message.content
```

### Fallback Response System

Intelligent fallback responses for common workplace queries:

- **HR Queries**: Benefits, payroll, leave requests
- **IT Support**: Technical issues, password resets
- **Employee Portal**: Navigation, profile management
- **General Help**: Workplace information

### Custom AI Provider Integration

To add a custom AI provider:

1. **Create Provider Class**
```python
class CustomAIProvider:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def generate_response(self, messages, config):
        # Implement your AI provider logic
        pass
```

2. **Update AIService**
```python
def generate_response(self, chat_session, user_message):
    if self.custom_ai_key:
        provider = CustomAIProvider(self.custom_ai_key)
        return provider.generate_response(messages, config)
    # ... existing logic
```

### Context Management

The system maintains conversation context:

```python
# Build conversation context
messages = [{"role": "system", "content": config.system_prompt}]

# Add recent chat history (last 10 messages)
recent_messages = chat_session.messages.order_by('-created_at')[:10]
for msg in reversed(recent_messages):
    if msg.message_type == 'user':
        messages.append({"role": "user", "content": msg.content})
    elif msg.message_type == 'assistant':
        messages.append({"role": "assistant", "content": msg.content})
```

## Security Features

### Authentication & Authorization

- **Token-based Authentication**: Secure API access with DRF tokens
- **Session Authentication**: WebSocket authentication via Django sessions
- **User Permissions**: Role-based access control (HR, IT Support)
- **Data Isolation**: Users can only access their own chat data

### Input Validation

- **Serializer Validation**: All API inputs validated through DRF serializers
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **XSS Protection**: Content sanitization and proper escaping
- **CSRF Protection**: Cross-site request forgery protection

### Security Headers

```python
# Security middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ... other middleware
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Rate Limiting

Implement rate limiting for API endpoints:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/m', method='POST')
def send_message_view(request):
    # Message sending logic
    pass
```

### Data Encryption

- **Password Hashing**: Django's built-in password hashing
- **Token Security**: Secure token generation and storage
- **Database Encryption**: PostgreSQL encryption at rest
- **Transport Security**: HTTPS/WSS in production

## Background Tasks

### Celery Configuration

Background tasks for analytics and maintenance:

```python
# celery_app.py
from celery import Celery

app = Celery('elariis_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Available Tasks

#### Update Chat Analytics
```python
@shared_task
def update_chat_analytics(chat_session_id):
    """Update analytics for a chat session"""
    # Calculate message counts, response times, etc.
```

#### Cleanup Old Sessions
```python
@shared_task
def cleanup_old_sessions():
    """Clean up old inactive chat sessions"""
    cutoff_date = timezone.now() - timedelta(days=30)
    old_sessions = ChatSession.objects.filter(
        is_active=False,
        updated_at__lt=cutoff_date
    )
    old_sessions.delete()
```

#### Daily Reports
```python
@shared_task
def generate_daily_report():
    """Generate daily analytics report"""
    # Generate usage statistics
```

### Task Scheduling

Configure periodic tasks in `settings.py`:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-sessions': {
        'task': 'chatbot.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'daily-report': {
        'task': 'chatbot.tasks.generate_daily_report',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}
```

## Monitoring & Analytics

### Logging Configuration

Comprehensive logging setup:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'chatbot.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'chatbot': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Analytics Tracking

The system tracks:
- **Message Counts**: User and assistant messages per session
- **Response Times**: Average AI response time
- **User Satisfaction**: Rating system for chat quality
- **Usage Patterns**: Peak usage times and popular queries
- **Error Rates**: Failed requests and error patterns

### Health Checks

Implement health check endpoints:

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """System health check"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'celery': check_celery_workers()
    })
```

## Frontend Integration

### React Integration Example

```javascript
// API Service
class ChatAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async createSession(title) {
    const response = await fetch(`${this.baseURL}/api/v1/chat/sessions/`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title })
    });
    return response.json();
  }

  async getSessions() {
    const response = await fetch(`${this.baseURL}/api/v1/chat/sessions/`, {
      headers: {
        'Authorization': `Token ${this.token}`
      }
    });
    return response.json();
  }

  async sendMessage(sessionId, content) {
    const response = await fetch(
      `${this.baseURL}/api/v1/chat/sessions/${sessionId}/send_message/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Token ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content })
      }
    );
    return response.json();
  }
}

// React Hook
function useChat(sessionId) {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    if (sessionId) {
      connectWebSocket();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId]);

  const connectWebSocket = () => {
    wsRef.current = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}/`);
    
    wsRef.current.onopen = () => {
      setIsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'message') {
        setMessages(prev => [...prev, data.message]);
      }
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
    };
  };

  const sendMessage = (content) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: 'message',
        content
      }));
    }
  };

  return { messages, isConnected, sendMessage };
}
```

### Authentication Flow

```javascript
// Login component
function Login() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  
  const handleLogin = async (e) => {
    e.preventDefault();
    
    const response = await fetch('/api/v1/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    });
    
    if (response.ok) {
      const { token, user } = await response.json();
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      // Redirect to chat
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="Username"
        value={credentials.username}
        onChange={(e) => setCredentials({
          ...credentials,
          username: e.target.value
        })}
      />
      <input
        type="password"
        placeholder="Password"
        value={credentials.password}
        onChange={(e) => setCredentials({
          ...credentials,
          password: e.target.value
        })}
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

## Deployment

### Production Settings

Create `settings_production.py`:

```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Docker Production

```dockerfile
# Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "elariis_backend.asgi:application"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Environment Variables for Production

```env
# Production environment
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (managed service recommended)
DB_NAME=elariis_prod
DB_USER=elariis_user
DB_PASSWORD=secure-password
DB_HOST=your-db-host.com
DB_PORT=5432

# Redis (managed service recommended)
REDIS_URL=redis://your-redis-host:6379

# AI Services
OPENAI_API_KEY=your-production-openai-key

# Email (for notifications)
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

## Development

### Setting Up Development Environment

1. **Install Development Dependencies**
```bash
pip install -r requirements-dev.txt
```

2. **Pre-commit Hooks**
```bash
pre-commit install
```

3. **Code Formatting**
```bash
# Format code
black .

# Sort imports
isort .

# Check style
flake8 .
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test chatbot

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name 0001
```

### Custom Management Commands

Create custom commands in `management/commands/`:

```python
# chatbot/management/commands/setup_ai_config.py
from django.core.management.base import BaseCommand
from chatbot.models import AIConfiguration

class Command(BaseCommand):
    help = 'Setup default AI configuration'

    def handle(self, *args, **options):
        config, created = AIConfiguration.objects.get_or_create(
            name='default',
            defaults={
                'model_name': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 1000,
                'system_prompt': 'You are a helpful AI assistant...'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created default AI configuration')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Default AI configuration already exists')
            )
```

Run with:
```bash
python manage.py setup_ai_config
```

## Troubleshooting

### Common Issues

#### WebSocket Connection Failed
```
Error: WebSocket connection failed
```

**Solutions:**
1. Check if Redis is running: `redis-cli ping`
2. Verify CHANNEL_LAYERS configuration
3. Ensure ASGI server is running (Daphne)
4. Check firewall settings for WebSocket ports

#### Database Connection Error
```
django.db.utils.OperationalError: could not connect to server
```

**Solutions:**
1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Ensure database exists: `createdb elariis_chatbot`
4. Check network connectivity to database host

#### Celery Worker Not Starting
```
[ERROR/MainProcess] consumer: Cannot connect to redis://localhost:6379
```

**Solutions:**
1. Start Redis server: `redis-server`
2. Check Redis URL in settings
3. Verify Redis is accessible: `redis-cli ping`
4. Check firewall settings

#### OpenAI API Errors
```
openai.error.AuthenticationError: Invalid API key
```

**Solutions:**
1. Verify OpenAI API key in `.env`
2. Check API key permissions and billing
3. Test with fallback responses (remove API key)
4. Check rate limits and quotas

### Debug Mode

Enable debug logging:

```python
# settings.py
LOGGING = {
    # ... existing config
    'loggers': {
        'chatbot': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',  # Change to DEBUG
            'propagate': True,
        },
        'django.channels': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Performance Issues

#### Slow Database Queries
1. Enable query logging:
```python
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}
```

2. Add database indexes:
```python
class Meta:
    indexes = [
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['is_active', 'updated_at']),
    ]
```

#### Memory Usage
1. Monitor with: `docker stats` or `htop`
2. Optimize queryset usage:
```python
# Use select_related for foreign keys
sessions = ChatSession.objects.select_related('user').all()

# Use prefetch_related for reverse foreign keys
sessions = ChatSession.objects.prefetch_related('messages').all()
```

3. Implement pagination for large datasets

#### WebSocket Performance
1. Monitor connection count
2. Implement connection pooling
3. Use Redis clustering for high load
4. Consider WebSocket load balancing

### Monitoring Commands

```bash
# Check system resources
htop
df -h
free -m

# Monitor Django processes
ps aux | grep python

# Check Redis
redis-cli info
redis-cli monitor

# Monitor PostgreSQL
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check logs
tail -f chatbot.log
docker-compose logs -f web
```

## Contributing

### Code Style Guidelines

1. **Python Code Style**
   - Follow PEP 8
   - Use Black for formatting
   - Maximum line length: 88 characters
   - Use type hints where appropriate

2. **Django Best Practices**
   - Use Django's built-in features
   - Follow Django naming conventions
   - Write comprehensive tests
   - Use proper error handling

3. **API Design**
   - RESTful endpoints
   - Consistent response formats
   - Proper HTTP status codes
   - Comprehensive documentation

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run test suite: `python manage.py test`
5. Format code: `black . && isort .`
6. Commit changes: `git commit -m "Add new feature"`
7. Push to branch: `git push origin feature/new-feature`
8. Create Pull Request

### Testing Guidelines

```python
# Test example
from django.test import TestCase
from django.contrib.auth import get_user_model
from chatbot.models import ChatSession, Message

User = get_user_model()

class ChatSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_chat_session(self):
        session = ChatSession.objects.create(
            user=self.user,
            session_id='test-uuid',
            title='Test Session'
        )
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)

    def test_send_message(self):
        session = ChatSession.objects.create(
            user=self.user,
            session_id='test-uuid'
        )
        
        message = Message.objects.create(
            chat_session=session,
            message_type='user',
            content='Test message'
        )
        
        self.assertEqual(message.chat_session, session)
        self.assertEqual(message.content, 'Test message')
```

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review Django and DRF documentation
- Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintainer**: Development Team