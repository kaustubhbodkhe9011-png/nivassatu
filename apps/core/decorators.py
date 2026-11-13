from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from apps.accounts.models import UserRole

def role_required(allowed_roles):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    If not, redirects to their assigned dashboard with an error message.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            
            # Superusers always have secretary level access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role not in allowed_roles:
                messages.error(request, "Access denied: You do not have permission to view that page.")
                return redirect("core:dashboard")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def secretary_required(view_func):
    return role_required([UserRole.SECRETARY])(view_func)

def resident_required(view_func):
    return role_required([UserRole.RESIDENT, UserRole.SECRETARY])(view_func)

def staff_required(view_func):
    return role_required([UserRole.STAFF, UserRole.SECRETARY])(view_func)

