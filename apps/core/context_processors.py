from apps.society.models import Society

def society_context(request):
    """
    Supplies global branding and user flat/role context to all templates.
    """
    soc = Society.objects.first()
    soc_name = soc.name if soc else "Nivas Residences CHS"
    
    context = {
        "APP_NAME": "NivasSetu",
        "APP_TAGLINE": "Housing Society Grievance & Dues Transparency",
        "SOCIETY_NAME": soc_name,
    }
    
    if request.user.is_authenticated:
        context["is_secretary"] = request.user.is_secretary
        context["is_resident"] = request.user.is_resident
        context["is_staff"] = request.user.is_staff_member
        
        # If resident, fetch primary active flat
        if hasattr(request.user, "resident_profiles"):
            primary_profile = request.user.resident_profiles.filter(is_active=True).select_related("flat__building").first()
            if primary_profile:
                context["current_flat"] = primary_profile.flat
                context["current_occupancy"] = primary_profile.occupancy_type
    
    return context
