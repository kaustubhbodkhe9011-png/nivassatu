"""
Complaints App Models: Complaint Categories, Complaints, Comments, Status History, and Feedback.
Follows strict 3NF design and SLA tracking rules.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random


class Priority(models.TextChoices):
    LOW = "LOW", "Low (72h SLA)"
    MEDIUM = "MEDIUM", "Medium (48h SLA)"
    HIGH = "HIGH", "High (24h SLA)"
    URGENT = "URGENT", "Urgent (12h SLA)"


class ComplaintStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    ASSIGNED = "ASSIGNED", "Assigned"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"
    REOPENED = "REOPENED", "Reopened"


class ComplaintCategory(models.Model):
    """
    Standard grievance categories in housing societies.
    """
    name = models.CharField(max_length=60, unique=True, help_text="e.g. Plumbing, Electrical, Lift")
    description = models.TextField(blank=True)
    default_sla_hours = models.PositiveIntegerField(
        default=48,
        help_text="Default SLA duration in hours for this category"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Complaint Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Complaint(models.Model):
    """
    Core Grievance Ticket Model.
    Tracks state transitions, SLA deadlines, assignments and resolutions.
    """
    ticket_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Unique human-readable ticket code e.g. TKT-202611-0001"
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="raised_complaints"
    )
    flat = models.ForeignKey(
        "society.Flat",
        on_delete=models.CASCADE,
        related_name="complaints",
        help_text="The affected flat unit"
    )
    category = models.ForeignKey(
        ComplaintCategory,
        on_delete=models.PROTECT,
        related_name="complaints"
    )
    assigned_to = models.ForeignKey(
        "society.StaffProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints"
    )
    title = models.CharField(max_length=150, help_text="Brief issue summary")
    description = models.TextField(help_text="Detailed problem explanation")
    priority = models.CharField(
        max_length=15,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=20,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.OPEN,
        db_index=True
    )
    photo = models.ImageField(upload_to="complaints/%Y/%m/", null=True, blank=True)
    sla_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Calculated deadline based on priority SLA"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    reopened_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        # Generate sequential ticket number if missing
        if not self.ticket_number:
            year_month = timezone.now().strftime("%Y%m")
            rand_suffix = random.randint(1000, 9999)
            self.ticket_number = f"TKT-{year_month}-{rand_suffix}"

        # Calculate SLA deadline on creation
        if not self.sla_deadline:
            sla_map = {
                Priority.URGENT: 12,
                Priority.HIGH: 24,
                Priority.MEDIUM: 48,
                Priority.LOW: 72,
            }
            hours = sla_map.get(self.priority, 48)
            self.sla_deadline = timezone.now() + timedelta(hours=hours)

        super().save(*args, **kwargs)

        # Record initial status in history
        if is_new:
            ComplaintStatusHistory.objects.create(
                complaint=self,
                changed_by=self.raised_by,
                from_status="",
                to_status=self.status,
                remarks="Complaint registered into system."
            )

    @property
    def is_overdue(self):
        """Flag true if past SLA deadline and not yet resolved or closed."""
        if self.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]:
            return False
        if self.sla_deadline and timezone.now() > self.sla_deadline:
            return True
        return False

    @property
    def can_reopen(self):
        """Resident can reopen if status is RESOLVED and resolved within the last 7 days."""
        if self.status != ComplaintStatus.RESOLVED:
            return False
        if not self.resolved_at:
            return True
        return timezone.now() <= (self.resolved_at + timedelta(days=7))

    def get_status_badge_class(self):
        badges = {
            ComplaintStatus.OPEN: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
            ComplaintStatus.ASSIGNED: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300",
            ComplaintStatus.IN_PROGRESS: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
            ComplaintStatus.RESOLVED: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
            ComplaintStatus.CLOSED: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300",
            ComplaintStatus.REOPENED: "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300",
        }
        return badges.get(self.status, "bg-gray-100 text-gray-800")

    def __str__(self):
        return f"[{self.ticket_number}] {self.title} ({self.get_status_display()})"


class ComplaintStatusHistory(models.Model):
    """
    Immutable audit history of status transitions.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.complaint.ticket_number}: {self.from_status} -> {self.to_status}"


class ComplaintComment(models.Model):
    """
    Communication feed on the ticket between resident, staff, and secretary.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal notes visible only to Secretary & Staff"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.complaint.ticket_number}"


class ComplaintFeedback(models.Model):
    """
    Resident satisfaction rating and feedback post-resolution.
    """
    complaint = models.OneToOneField(
        Complaint,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        help_text="1 (Poor) to 5 (Excellent)"
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.ticket_number} - {self.rating} Stars"

