from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.core.decorators import secretary_required
from .models import AuditLog

@login_required
@secretary_required
def audit_trail_view(request):
    """Secretary-only audit log browser."""
    logs = AuditLog.objects.select_related("actor").all()[:100]
    return render(request, "audit/audit_trail.html", {"logs": logs})

