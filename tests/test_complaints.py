import pytest
from django.utils import timezone
from datetime import timedelta
from apps.complaints.models import Complaint, ComplaintCategory, ComplaintStatus, Priority, ComplaintStatusHistory
from apps.society.models import Society, Building, Flat, FlatType, ResidentProfile, OccupancyType, StaffProfile
from apps.accounts.models import User, UserRole

@pytest.fixture
def complaint_fixture(db, resident_user, staff_user):
    soc = Society.objects.create(name="Nivas Residences CHS", registration_number="MH/2026/99")
    wing = Building.objects.create(society=soc, name="Wing A", total_floors=5)
    flat = Flat.objects.create(building=wing, flat_number="202", floor=2, square_feet=750)
    ResidentProfile.objects.create(user=resident_user, flat=flat, occupancy_type=OccupancyType.OWNER)
    staff_profile = StaffProfile.objects.create(user=staff_user, employee_code="STF-PLUMB", specialty="Plumber")
    category = ComplaintCategory.objects.create(name="Plumbing", default_sla_hours=48)
    return {
        "soc": soc,
        "flat": flat,
        "staff": staff_profile,
        "category": category,
        "resident": resident_user,
    }

@pytest.mark.django_db
def test_complaint_creation_and_sla(complaint_fixture):
    c = Complaint.objects.create(
        raised_by=complaint_fixture["resident"],
        flat=complaint_fixture["flat"],
        category=complaint_fixture["category"],
        title="Pipe burst in bathroom",
        description="Water gushing continuously.",
        priority=Priority.URGENT,
    )
    assert c.ticket_number.startswith("TKT-")
    assert c.status == ComplaintStatus.OPEN
    # Urgent SLA is 12 hours
    diff = c.sla_deadline - c.created_at
    assert 11 <= diff.total_seconds() / 3600 <= 13
    assert ComplaintStatusHistory.objects.filter(complaint=c).count() == 1

@pytest.mark.django_db
def test_workflow_state_machine_and_reopen(complaint_fixture):
    c = Complaint.objects.create(
        raised_by=complaint_fixture["resident"],
        flat=complaint_fixture["flat"],
        category=complaint_fixture["category"],
        title="Tap replacement",
        description="Needs washer change",
        priority=Priority.LOW,
    )
    # Assign staff
    c.assigned_to = complaint_fixture["staff"]
    c.status = ComplaintStatus.ASSIGNED
    c.save()

    # In progress
    c.status = ComplaintStatus.IN_PROGRESS
    c.save()

    # Resolved
    c.status = ComplaintStatus.RESOLVED
    c.resolved_at = timezone.now()
    c.save()

    assert c.can_reopen is True

    # Check 7-day boundary expiration
    c.resolved_at = timezone.now() - timedelta(days=8)
    assert c.can_reopen is False

@pytest.mark.django_db
def test_resident_isolation_access(client, resident_user, staff_user, complaint_fixture):
    # Other resident
    other_user = User.objects.create_user(username="other_res", password="password123", role=UserRole.RESIDENT)
    c = Complaint.objects.create(
        raised_by=complaint_fixture["resident"],
        flat=complaint_fixture["flat"],
        category=complaint_fixture["category"],
        title="Private leak",
        description="Private leak details",
    )

    client.login(username="other_res", password="password123")
    res = client.get(f"/complaints/{c.ticket_number}/")
    # Must deny access and redirect
    assert res.status_code == 302
    assert res.url == "/complaints/"

