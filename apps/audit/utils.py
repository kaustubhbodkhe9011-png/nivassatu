from .models import AuditLog

def record_audit(actor, action, target_model, target_object_id, summary, request=None):
    """Utility helper to record an audit action."""
    ip = None
    if request:
        ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_model=target_model,
        target_object_id=str(target_object_id),
        summary=summary,
        ip_address=ip
    )

