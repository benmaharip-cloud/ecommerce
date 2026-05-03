from django.contrib import admin
from .models import ChatRoom, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("sender", "content", "created_at", "is_read")

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "message_count", "is_active", "created_at")
    list_editable = ("is_active",)
    inlines = [ChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender", "content_preview", "is_read", "created_at")
    list_filter = ("is_read", "is_bot")
    search_fields = ("content", "sender__email")

    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = "Message"
