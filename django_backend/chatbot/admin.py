from django.contrib import admin
from .models import ChatSession, Message, AIConfiguration, ChatAnalytics

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['session_id', 'user__username', 'user__email', 'title']
    readonly_fields = ['session_id', 'created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_session', 'message_type', 'content_preview', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['content', 'chat_session__session_id', 'chat_session__user__username']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_name', 'temperature', 'max_tokens', 'is_active', 'created_at']
    list_filter = ['is_active', 'model_name', 'created_at']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['chat_session', 'total_messages', 'user_messages', 'assistant_messages', 'satisfaction_rating']
    list_filter = ['satisfaction_rating', 'created_at']
    search_fields = ['chat_session__session_id', 'chat_session__user__username']
    readonly_fields = ['created_at', 'updated_at']