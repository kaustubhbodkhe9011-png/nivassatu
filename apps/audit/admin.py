from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor", "action", "target_model", "target_object_id", "summary")
    list_filter = ("action", "target_model", "timestamp")
    search_fields = ("summary", "target_object_id", "actor__username")

