import pytest
from decimal import Decimal
from django.utils import timezone
from apps.dues.models import MaintenancePlan, DuesRecord, Payment, DuesStatus, PaymentMode
from apps.society.models import Society, Building, Flat

@pytest.fixture
def dues_fixture(db, resident_user):
    soc = Society.objects.create(name="Shanti Heights CHS", registration_number="MH/2026/07")
    bldg = Building.objects.create(society=soc, name="Wing B")
    flat = Flat.objects.create(building=bldg, flat_number="501", floor=5, square_feet=1000.00)
    plan = MaintenancePlan.objects.create(
        base_rate_per_sqft=Decimal("2.00"),
        fixed_charge=Decimal("500.00"),
        late_fine_rate=Decimal("100.00")
    )
    return {
        "flat": flat,
        "plan": plan,
        "user": resident_user,
    }

@pytest.mark.django_db
def test_dues_calculation_and_payment_status(dues_fixture):
    flat = dues_fixture["flat"]
    plan = dues_fixture["plan"]
    user = dues_fixture["user"]

    # 1000 sq.ft * 2.00 + 500 = 2500.00
    calculated_due = plan.calculate_due_for_flat(flat)
    assert calculated_due == Decimal("2500.00")

    due_record = DuesRecord.objects.create(
        flat=flat,
        plan=plan,
        billing_month="November 2026",
        principal_amount=calculated_due,
        total_due=calculated_due,
        due_date=timezone.now().date(),
        status=DuesStatus.PENDING
    )
    assert due_record.balance_remaining == Decimal("2500.00")

    # Partial payment of 1000
    p1 = Payment.objects.create(
        dues_record=due_record,
        recorded_by=user,
        amount=Decimal("1000.00"),
        payment_mode=PaymentMode.UPI,
        transaction_reference="UPI/123456789",
        payment_date=timezone.now().date()
    )
    assert p1.receipt_number.startswith("REC-")
    due_record.refresh_from_db()
    assert due_record.amount_paid == Decimal("1000.00")
    assert due_record.status == DuesStatus.PARTIAL
    assert due_record.balance_remaining == Decimal("1500.00")

    # Full settlement of remaining 1500
    Payment.objects.create(
        dues_record=due_record,
        recorded_by=user,
        amount=Decimal("1500.00"),
        payment_mode=PaymentMode.CHEQUE,
        transaction_reference="CHQ/001122",
        payment_date=timezone.now().date()
    )
    due_record.refresh_from_db()
    assert due_record.amount_paid == Decimal("2500.00")
    assert due_record.status == DuesStatus.PAID
    assert due_record.balance_remaining == Decimal("0.00")

