from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.core.decorators import secretary_required
from .models import Flat, Building, ResidentProfile, StaffProfile
from .forms import FlatForm, AssignResidentForm

@login_required
@secretary_required
def flat_list_view(request):
    """Lists all flats grouped by building wings with current occupancy."""
    flats = Flat.objects.select_related("building").prefetch_related("resident_profiles__user").all()
    buildings = Building.objects.all()
    
    building_filter = request.GET.get("building")
    if building_filter:
        flats = flats.filter(building_id=building_filter)

    return render(request, "society/flat_list.html", {
        "flats": flats,
        "buildings": buildings,
        "selected_building": building_filter,
    })

@login_required
@secretary_required
def resident_list_view(request):
    """Lists all registered residents, occupancy assignments, and staff technicians."""
    residents = ResidentProfile.objects.select_related("user", "flat__building").all()
    staff_members = StaffProfile.objects.select_related("user").all()

    return render(request, "society/resident_list.html", {
        "residents": residents,
        "staff_members": staff_members,
    })

@login_required
@secretary_required
def add_flat_view(request):
    """Allows secretary to add a new flat to a wing."""
    if request.method == "POST":
        form = FlatForm(request.POST)
        if form.is_valid():
            flat = form.save()
            messages.success(request, f"Flat {flat.full_name} added successfully.")
            return redirect("society:flats")
    else:
        form = FlatForm()
    return render(request, "society/flat_form.html", {"form": form, "title": "Add Flat"})

@login_required
@secretary_required
def assign_resident_view(request):
    """Maps a resident user to a specific flat."""
    if request.method == "POST":
        form = AssignResidentForm(request.POST)
        if form.is_valid():
            profile = form.save()
            messages.success(request, f"Assigned {profile.user.get_full_name() or profile.user.username} to {profile.flat.full_name}.")
            return redirect("society:residents")
    else:
        form = AssignResidentForm()
    return render(request, "society/assign_resident.html", {"form": form})

