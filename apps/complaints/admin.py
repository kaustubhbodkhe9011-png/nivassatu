from django.contrib import admin
from .models import ComplaintCategory, Complaint, ComplaintStatusHistory, ComplaintComment, ComplaintFeedback

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "default_sla_hours", "is_active")

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "title", "raised_by", "flat", "category", "priority", "status", "is_overdue", "created_at")
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = ("ticket_number", "title", "description", "raised_by__username", "flat__flat_number")

@admin.register(ComplaintStatusHistory)
class ComplaintStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("complaint", "from_status", "to_status", "changed_by", "created_at")

@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    list_display = ("complaint", "author", "is_internal", "created_at")

@admin.register(ComplaintFeedback)
class ComplaintFeedbackAdmin(admin.ModelAdmin):
    list_display = ("complaint", "rating", "resident", "created_at")

