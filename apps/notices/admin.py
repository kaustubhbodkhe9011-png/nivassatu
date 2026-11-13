from django.contrib import admin
from .models import Notice, NoticeAcknowledgement

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_pinned", "published_by", "created_at")
    list_filter = ("category", "is_pinned", "created_at")
    search_fields = ("title", "content")

@admin.register(NoticeAcknowledgement)
class NoticeAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ("notice", "user", "acknowledged_at")

