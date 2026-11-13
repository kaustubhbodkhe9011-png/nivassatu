import pytest
from apps.audit.utils import record_audit
from apps.audit.models import AuditLog, AuditAction

@pytest.mark.django_db
def test_audit_logging_record(secretary_user):
    log = record_audit(
        actor=secretary_user,
        action=AuditAction.STATUS_CHANGE,
        target_model="Complaint",
        target_object_id="TKT-202611-1001",
        summary="Transitioned status to RESOLVED"
    )
    assert log.actor == secretary_user
    assert log.action == AuditAction.STATUS_CHANGE
    assert AuditLog.objects.count() == 1

@pytest.mark.django_db
def test_reports_views_and_csv_export(client, secretary_user, resident_user):
    client.login(username="sec_test", password="password123")
    
    # Reports overview
    res = client.get("/reports/")
    assert res.status_code == 200

    # CSV exports
    res_comp = client.get("/reports/export/complaints/")
    assert res_comp.status_code == 200
    assert res_comp["Content-Type"] == "text/csv"

    res_dues = client.get("/reports/export/dues/")
    assert res_dues.status_code == 200
    assert res_dues["Content-Type"] == "text/csv"
    client.logout()

    # Resident cannot access reports
    client.login(username="res_test", password="password123")
    res_blocked = client.get("/reports/")
    assert res_blocked.status_code == 302

