from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.decorators import secretary_required
from .models import DuesRecord, Payment, MaintenancePlan, DuesStatus
from .forms import PaymentForm
from apps.society.models import Flat

@login_required
def dues_list_view(request):
    """
    Shows maintenance records.
    Secretary sees all flats.
    Resident sees only their occupied flats.
    """
    user = request.user
    if user.is_secretary:
        dues = DuesRecord.objects.select_related("flat__building", "plan").all()
    else:
        user_flats = user.resident_profiles.filter(is_active=True).values_list("flat_id", flat=True)
        dues = DuesRecord.objects.filter(flat_id__in=user_flats).select_related("flat__building", "plan")

    status_filter = request.GET.get("status")
    if status_filter:
        dues = dues.filter(status=status_filter)

    return render(request, "dues/dues_list.html", {
        "dues": dues,
        "status_choices": DuesStatus.choices,
        "selected_status": status_filter,
    })

@login_required
@secretary_required
def generate_dues_view(request):
    """Batch generates maintenance bills for all flats for the current month."""
    if request.method == "POST":
        current_month = timezone.now().strftime("%B %Y")
        plan = MaintenancePlan.objects.first()
        if not plan:
            plan = MaintenancePlan.objects.create()

        flats = Flat.objects.all()
        created_count = 0
        due_date = timezone.now().date() + timedelta(days=15)

        for flat in flats:
            amount = plan.calculate_due_for_flat(flat)
            _, created = DuesRecord.objects.get_or_create(
                flat=flat,
                billing_month=current_month,
                defaults={
                    "plan": plan,
                    "principal_amount": amount,
                    "total_due": amount,
                    "due_date": due_date,
                    "status": DuesStatus.PENDING,
                }
            )
            if created:
                created_count += 1

        messages.success(request, f"Generated maintenance dues for {created_count} flats ({current_month}).")
        return redirect("dues:list")
    return render(request, "dues/generate_dues.html")

@login_required
def record_payment_view(request, dues_id):
    """Records payment (Cash, UPI, Cheque) against a dues bill."""
    due = get_object_or_404(DuesRecord, id=dues_id)

    # Resident can only pay their own flat dues
    if not request.user.is_secretary:
        user_flats = request.user.resident_profiles.filter(is_active=True).values_list("flat_id", flat=True)
        if due.flat_id not in user_flats:
            messages.error(request, "Permission denied.")
            return redirect("dues:list")

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.dues_record = due
            payment.recorded_by = request.user
            payment.save()
            messages.success(request, f"Payment of ₹{payment.amount} recorded! Receipt: {payment.receipt_number}")
            return redirect("dues:receipt", receipt_number=payment.receipt_number)
    else:
        form = PaymentForm(initial={
            "amount": due.balance_remaining,
            "payment_date": timezone.now().date()
        })

    return render(request, "dues/record_payment.html", {"form": form, "due": due})

@login_required
def receipt_view(request, receipt_number):
    """Printable invoice receipt page."""
    payment = get_object_or_404(
        Payment.objects.select_related("dues_record__flat__building", "recorded_by"),
        receipt_number=receipt_number
    )
    return render(request, "dues/receipt.html", {"payment": payment})

