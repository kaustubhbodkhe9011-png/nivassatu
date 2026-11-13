"""
Notices App Models: Broadcast announcements, pinning, and resident acknowledgements.
"""
from django.db import models
from django.conf import settings


class NoticeCategory(models.TextChoices):
    GENERAL = "GENERAL", "General Announcement"
    MAINTENANCE = "MAINTENANCE", "Water / Power Maintenance"
    MEETING = "MEETING", "AGM / Society Meeting"
    SECURITY = "SECURITY", "Security Advisory"
    CELEBRATION = "CELEBRATION", "Festival & Events"


class Notice(models.Model):
    """
    Official Society Notice.
    """
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="published_notices"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=NoticeCategory.choices,
        default=NoticeCategory.GENERAL
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pinned notices appear highlighted at the top"
    )
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def is_acknowledged_by(self, user):
        if not user.is_authenticated:
            return False
        return self.acknowledgements.filter(user=user).exists()

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class NoticeAcknowledgement(models.Model):
    """
    Read receipt proving resident has acknowledged the notice.
    """
    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name="acknowledgements"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notice_acknowledgements"
    )
    acknowledged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("notice", "user")

    def __str__(self):
        return f"{self.user.username} read {self.notice.title}"

