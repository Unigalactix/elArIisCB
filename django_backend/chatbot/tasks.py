from celery import shared_task
from .models import ChatSession, ChatAnalytics, Message
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('chatbot')

@shared_task
def update_chat_analytics(chat_session_id):
    """Update analytics for a chat session"""
    try:
        chat_session = ChatSession.objects.get(id=chat_session_id)
        analytics, created = ChatAnalytics.objects.get_or_create(
            chat_session=chat_session
        )
        
        messages = chat_session.messages.all()
        analytics.total_messages = messages.count()
        analytics.user_messages = messages.filter(message_type='user').count()
        analytics.assistant_messages = messages.filter(message_type='assistant').count()
        
        # Calculate average response time (simplified)
        user_messages = messages.filter(message_type='user').order_by('created_at')
        assistant_messages = messages.filter(message_type='assistant').order_by('created_at')
        
        if user_messages.exists() and assistant_messages.exists():
            total_response_time = 0
            response_count = 0
            
            for i, user_msg in enumerate(user_messages):
                try:
                    assistant_msg = assistant_messages.filter(
                        created_at__gt=user_msg.created_at
                    ).first()
                    if assistant_msg:
                        response_time = (assistant_msg.created_at - user_msg.created_at).total_seconds()
                        total_response_time += response_time
                        response_count += 1
                except:
                    continue
            
            if response_count > 0:
                analytics.average_response_time = total_response_time / response_count
        
        analytics.save()
        logger.info(f"Updated analytics for chat session {chat_session_id}")
        
    except ChatSession.DoesNotExist:
        logger.error(f"Chat session {chat_session_id} not found")
    except Exception as e:
        logger.error(f"Error updating analytics: {str(e)}")

@shared_task
def cleanup_old_sessions():
    """Clean up old inactive chat sessions"""
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        old_sessions = ChatSession.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_date
        )
        
        deleted_count = old_sessions.count()
        old_sessions.delete()
        
        logger.info(f"Cleaned up {deleted_count} old chat sessions")
        
    except Exception as e:
        logger.error(f"Error cleaning up old sessions: {str(e)}")

@shared_task
def generate_daily_report():
    """Generate daily analytics report"""
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get yesterday's stats
        sessions_created = ChatSession.objects.filter(
            created_at__date=yesterday
        ).count()
        
        messages_sent = Message.objects.filter(
            created_at__date=yesterday
        ).count()
        
        user_messages = Message.objects.filter(
            created_at__date=yesterday,
            message_type='user'
        ).count()
        
        assistant_messages = Message.objects.filter(
            created_at__date=yesterday,
            message_type='assistant'
        ).count()
        
        logger.info(f"Daily Report for {yesterday}:")
        logger.info(f"- Sessions created: {sessions_created}")
        logger.info(f"- Total messages: {messages_sent}")
        logger.info(f"- User messages: {user_messages}")
        logger.info(f"- Assistant messages: {assistant_messages}")
        
        # You can extend this to send email reports, save to database, etc.
        
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")