import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, F
from django.utils import timezone
from apps.core.decorators import secretary_required
from apps.complaints.models import Complaint, ComplaintStatus, ComplaintCategory
from apps.dues.models import DuesRecord, Payment

@login_required
@secretary_required
def reports_overview_view(request):
    """
    Analytics Dashboard with Chart.js datasets:
    1. Complaints by status (Open, In Progress, Resolved, Closed)
    2. Category distribution
    3. Maintenance dues collected vs pending
    """
    # Complaints metrics
    total_complaints = Complaint.objects.count()
    open_complaints = Complaint.objects.filter(status__in=[ComplaintStatus.OPEN, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.REOPENED]).count()
    resolved_complaints = Complaint.objects.filter(status__in=[ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED]).count()
    
    # Overdue count
    overdue_complaints = [c for c in Complaint.objects.all() if c.is_overdue]
    overdue_count = len(overdue_complaints)

    # Categories breakdown
    categories_data = ComplaintCategory.objects.annotate(ticket_count=Count("complaints")).values("name", "ticket_count")
    cat_labels = [c["name"] for c in categories_data]
    cat_counts = [c["ticket_count"] for c in categories_data]

    # Dues metrics
    dues_agg = DuesRecord.objects.aggregate(
        total_billed=Sum("total_due"),
        total_paid=Sum("amount_paid")
    )
    total_billed = dues_agg["total_billed"] or 0
    total_paid = dues_agg["total_paid"] or 0
    total_pending = max(0, total_billed - total_paid)

    return render(request, "reports/overview.html", {
        "total_complaints": total_complaints,
        "open_complaints": open_complaints,
        "resolved_complaints": resolved_complaints,
        "overdue_count": overdue_count,
        "cat_labels": cat_labels,
        "cat_counts": cat_counts,
        "total_billed": total_billed,
        "total_paid": total_paid,
        "total_pending": total_pending,
    })

@login_required
@secretary_required
def export_complaints_csv(request):
    """Generates CSV download for complaints."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="nivassetu_complaints_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Ticket Number", "Flat", "Raised By", "Category", "Priority", "Status", "SLA Deadline", "Created At"])

    for c in Complaint.objects.select_related("flat__building", "raised_by", "category").all():
        writer.writerow([
            c.ticket_number,
            c.flat.full_name,
            c.raised_by.get_full_name() or c.raised_by.username,
            c.category.name,
            c.get_priority_display(),
            c.get_status_display(),
            c.sla_deadline.strftime("%Y-%m-%d %H:%M") if c.sla_deadline else "",
            c.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    return response

@login_required
@secretary_required
def export_dues_csv(request):
    """Generates CSV download for dues ledger."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="nivassetu_maintenance_dues.csv"'

    writer = csv.writer(response)
    writer.writerow(["Flat", "Month", "Total Due (INR)", "Amount Paid (INR)", "Balance (INR)", "Status", "Due Date"])

    for d in DuesRecord.objects.select_related("flat__building").all():
        writer.writerow([
            d.flat.full_name,
            d.billing_month,
            d.total_due,
            d.amount_paid,
            d.balance_remaining,
            d.get_status_display(),
            d.due_date.strftime("%Y-%m-%d")
        ])
    return response

