"""
Audit App Models: Centralized immutable audit logs for sensitive operations.
"""
from django.db import models
from django.conf import settings


class AuditAction(models.TextChoices):
    CREATE = "CREATE", "Created"
    UPDATE = "UPDATE", "Updated"
    DELETE = "DELETE", "Deleted"
    STATUS_CHANGE = "STATUS_CHANGE", "Status Transition"
    PAYMENT = "PAYMENT", "Payment Settlement"


class AuditLog(models.Model):
    """
    Immutable audit log entry.
    """
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_actions"
    )
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    target_model = models.CharField(max_length=60)
    target_object_id = models.CharField(max_length=60)
    summary = models.TextField(help_text="Human-readable description of change")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.actor} - {self.action} on {self.target_model} #{self.target_object_id}"

