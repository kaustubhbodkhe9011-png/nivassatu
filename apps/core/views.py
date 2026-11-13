from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.models import UserRole

def landing_page(request):
    """Public showcase landing page with architecture, problem statement and demo shortcuts."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/landing.html")

@login_required
def dashboard_dispatcher(request):
    """Dispatches logged-in user to their specific role dashboard."""
    if request.user.is_secretary:
        return redirect("core:secretary_dashboard")
    elif request.user.is_staff_member:
        return redirect("core:staff_dashboard")
    else:
        return redirect("core:resident_dashboard")

@login_required
def secretary_dashboard(request):
    if not request.user.is_secretary:
        return redirect("core:dashboard")
    return render(request, "core/secretary_dashboard.html")

@login_required
def resident_dashboard(request):
    return render(request, "core/resident_dashboard.html")

@login_required
def staff_dashboard(request):
    return render(request, "core/staff_dashboard.html")

