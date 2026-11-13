import pytest
from apps.society.models import Society, Building, Flat, FlatType, ResidentProfile, OccupancyType, StaffProfile
from apps.accounts.models import User, UserRole

@pytest.fixture
def society_setup(db):
    soc = Society.objects.create(
        name="Nivas Residences CHS",
        registration_number="MH/MUM/2026/01",
        address="Film City Road, Goregaon East, Mumbai - 400063",
        contact_phone="+912228490000",
    )
    wing_a = Building.objects.create(society=soc, name="Wing A", total_floors=7)
    wing_b = Building.objects.create(society=soc, name="Wing B", total_floors=7)
    
    flat_101 = Flat.objects.create(
        building=wing_a,
        flat_number="101",
        floor=1,
        flat_type=FlatType.TWO_BHK,
        square_feet=850.00
    )
    return {
        "society": soc,
        "wing_a": wing_a,
        "wing_b": wing_b,
        "flat_101": flat_101,
    }

@pytest.mark.django_db
def test_society_structure_and_flat_naming(society_setup):
    flat = society_setup["flat_101"]
    assert flat.full_name == "Wing A-101"
    assert str(flat) == "Wing A - Flat 101"
    assert flat.square_feet == 850.00

@pytest.mark.django_db
def test_resident_occupancy_mapping(society_setup, resident_user):
    flat = society_setup["flat_101"]
    profile = ResidentProfile.objects.create(
        user=resident_user,
        flat=flat,
        occupancy_type=OccupancyType.OWNER,
        is_primary_contact=True,
        is_active=True
    )
    assert flat.get_current_occupant() == resident_user
    assert profile.occupancy_type == OccupancyType.OWNER

@pytest.mark.django_db
def test_staff_profile(staff_user):
    staff_profile = StaffProfile.objects.create(
        user=staff_user,
        employee_code="STF-01",
        specialty="Electrician",
        is_available=True
    )
    assert staff_profile.employee_code == "STF-01"
    assert staff_profile.specialty == "Electrician"
    assert staff_profile.is_available is True

@pytest.mark.django_db
def test_secretary_access_to_society_views(client, secretary_user, resident_user, society_setup):
    # Secretary can access flats directory
    client.login(username="sec_test", password="password123")
    res = client.get("/society/flats/")
    assert res.status_code == 200
    assert "Wing A-101" in res.content.decode() or "101" in res.content.decode()
    client.logout()

    # Resident is denied secretary-only views and redirected
    client.login(username="res_test", password="password123")
    res = client.get("/society/flats/")
    assert res.status_code == 302

