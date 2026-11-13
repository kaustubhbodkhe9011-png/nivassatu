import pytest
from apps.notices.models import Notice, NoticeCategory, NoticeAcknowledgement

@pytest.mark.django_db
def test_notice_creation_and_acknowledgement(secretary_user, resident_user):
    notice = Notice.objects.create(
        published_by=secretary_user,
        title="Lift Maintenance on Saturday",
        content="Passenger lift Wing A will be closed for servicing.",
        category=NoticeCategory.MAINTENANCE,
        is_pinned=True
    )
    assert notice.is_acknowledged_by(resident_user) is False

    NoticeAcknowledgement.objects.create(notice=notice, user=resident_user)
    assert notice.is_acknowledged_by(resident_user) is True

