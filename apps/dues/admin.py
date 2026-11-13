from django.contrib import admin
from .models import MaintenancePlan, DuesRecord, Payment

@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "base_rate_per_sqft", "fixed_charge", "late_fine_rate")

@admin.register(DuesRecord)
class DuesRecordAdmin(admin.ModelAdmin):
    list_display = ("flat", "billing_month", "total_due", "amount_paid", "status", "due_date")
    list_filter = ("status", "billing_month")
    search_fields = ("flat__flat_number", "flat__building__name")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "dues_record", "amount", "payment_mode", "payment_date", "recorded_by")
    list_filter = ("payment_mode", "payment_date")
    search_fields = ("receipt_number", "transaction_reference")

