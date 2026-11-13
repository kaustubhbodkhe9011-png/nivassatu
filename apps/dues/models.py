"""
Dues App Models: Maintenance Plans, Monthly Dues per Flat, and Payments with Receipts.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal
import random


class DuesStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PARTIAL = "PARTIAL", "Partially Paid"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"


class PaymentMode(models.TextChoices):
    UPI = "UPI", "UPI / Net Banking"
    CHEQUE = "CHEQUE", "Cheque / DD"
    CASH = "CASH", "Cash"


class MaintenancePlan(models.Model):
    """
    Society maintenance tariff rule.
    """
    name = models.CharField(max_length=100, default="Standard Society Maintenance")
    base_rate_per_sqft = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("2.50"),
        help_text="Maintenance rate in INR per sq.ft of carpet area"
    )
    fixed_charge = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("500.00"),
        help_text="Fixed charges for lift, security and sinking fund"
    )
    late_fine_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text="Penalty fine charged for payment after due date"
    )
    effective_from = models.DateField(auto_now_add=True)

    def calculate_due_for_flat(self, flat):
        sqft = Decimal(str(flat.square_feet))
        return (sqft * self.base_rate_per_sqft) + self.fixed_charge

    def __str__(self):
        return f"{self.name} (₹{self.base_rate_per_sqft}/sqft + ₹{self.fixed_charge})"


class DuesRecord(models.Model):
    """
    Monthly maintenance statement for a specific flat.
    """
    flat = models.ForeignKey(
        "society.Flat",
        on_delete=models.CASCADE,
        related_name="dues_records"
    )
    plan = models.ForeignKey(
        MaintenancePlan,
        on_delete=models.PROTECT,
        related_name="dues_records"
    )
    billing_month = models.CharField(
        max_length=20,
        help_text="e.g. November 2026",
        db_index=True
    )
    principal_amount = models.DecimalField(max_digits=8, decimal_places=2)
    late_fine = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    total_due = models.DecimalField(max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(
        max_length=20,
        choices=DuesStatus.choices,
        default=DuesStatus.PENDING
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("flat", "billing_month")
        ordering = ["-created_at"]

    @property
    def balance_remaining(self):
        return max(Decimal("0.00"), self.total_due - self.amount_paid)

    def update_status(self):
        if self.amount_paid >= self.total_due:
            self.status = DuesStatus.PAID
        elif self.amount_paid > Decimal("0.00"):
            self.status = DuesStatus.PARTIAL
        else:
            self.status = DuesStatus.PENDING
        self.save()

    def __str__(self):
        return f"{self.flat.full_name} - {self.billing_month} (₹{self.total_due})"


class Payment(models.Model):
    """
    Verified payment record against a maintenance bill.
    """
    dues_record = models.ForeignKey(
        DuesRecord,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="e.g. REC-202611-0012"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_mode = models.CharField(
        max_length=20,
        choices=PaymentMode.choices,
        default=PaymentMode.UPI
    )
    transaction_reference = models.CharField(
        max_length=60,
        blank=True,
        help_text="UPI Reference UTR, Cheque No, or Cash memo code"
    )
    payment_date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            rand_code = random.randint(1000, 9999)
            self.receipt_number = f"REC-{self.payment_date.strftime('%Y%m')}-{rand_code}"
        super().save(*args, **kwargs)
        # Update parent dues record
        self.dues_record.amount_paid += self.amount
        self.dues_record.update_status()

    def __str__(self):
        return f"[{self.receipt_number}] ₹{self.amount} for {self.dues_record.flat.full_name}"
