from django.contrib import admin
from .models import Society, Building, Flat, ResidentProfile, StaffProfile

@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number", "contact_phone", "contact_email")

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "society", "total_floors")
    list_filter = ("society",)

@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ("full_name", "building", "floor", "flat_type", "square_feet")
    list_filter = ("building", "flat_type")
    search_fields = ("flat_number", "building__name")

@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "flat", "occupancy_type", "is_primary_contact", "is_active")
    list_filter = ("occupancy_type", "is_active", "flat__building")
    search_fields = ("user__username", "user__first_name", "user__last_name", "flat__flat_number")

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "employee_code", "specialty", "is_available")
    list_filter = ("specialty", "is_available")
    search_fields = ("user__username", "employee_code", "specialty")

