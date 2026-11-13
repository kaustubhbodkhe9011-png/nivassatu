import pytest
from apps.accounts.models import User, UserRole

@pytest.fixture
def secretary_user(db):
    return User.objects.create_user(
        username="sec_test",
        password="password123",
        role=UserRole.SECRETARY,
        first_name="Society",
        last_name="Secretary",
        phone_number="+919876543210",
    )

@pytest.fixture
def resident_user(db):
    return User.objects.create_user(
        username="res_test",
        password="password123",
        role=UserRole.RESIDENT,
        first_name="Ramesh",
        last_name="Sharma",
        phone_number="+919876543211",
    )

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff_test",
        password="password123",
        role=UserRole.STAFF,
        first_name="Shankar",
        last_name="Electrician",
        phone_number="+919876543212",
    )

