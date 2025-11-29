from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ['role', 'content', 'timestamp']
    readonly_fields = ['timestamp']
    ordering = ['timestamp']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'collection_name', 'message_count', 'created_at', 'updated_at', 'is_archived']
    list_filter = ['collection_name', 'is_archived', 'created_at', 'updated_at']
    search_fields = ['title', 'collection_name', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageInline]
    date_hierarchy = 'created_at'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'timestamp']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'conversation__title', 'conversation__user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'