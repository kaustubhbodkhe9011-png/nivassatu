import pytest
from django.urls import reverse
from apps.accounts.models import UserRole

@pytest.mark.django_db
def test_user_creation_and_roles(secretary_user, resident_user, staff_user):
    assert secretary_user.is_secretary is True
    assert secretary_user.is_resident is False
    assert secretary_user.role == UserRole.SECRETARY

    assert resident_user.is_resident is True
    assert resident_user.is_secretary is False
    assert resident_user.role == UserRole.RESIDENT

    assert staff_user.is_staff_member is True
    assert staff_user.role == UserRole.STAFF

@pytest.mark.django_db
def test_login_and_role_redirection(client, secretary_user, resident_user, staff_user):
    # Secretary login should route to secretary dashboard
    client.login(username="sec_test", password="password123")
    response = client.get(reverse("core:dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("core:secretary_dashboard")
    client.logout()

    # Resident login should route to resident dashboard
    client.login(username="res_test", password="password123")
    response = client.get(reverse("core:dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("core:resident_dashboard")
    client.logout()

    # Staff login should route to staff dashboard
    client.login(username="staff_test", password="password123")
    response = client.get(reverse("core:dashboard"))
    assert response.status_code == 302
    assert response.url == reverse("core:staff_dashboard")
    client.logout()

@pytest.mark.django_db
def test_unauthenticated_redirect(client):
    response = client.get(reverse("core:dashboard"))
    assert response.status_code == 302
    assert "/login/" in response.url

