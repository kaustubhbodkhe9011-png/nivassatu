"""
Society Setup Models: Society master, Buildings/Wings, Flats, and Resident/Staff mapping.
Strict 3NF design.
"""
from django.db import models
from django.conf import settings


class Society(models.Model):
    """
    Housing Society Master Entity.
    """
    name = models.CharField(max_length=150, help_text="e.g. Gokuldham Heights CHS")
    registration_number = models.CharField(
        max_length=60,
        unique=True,
        help_text="Society registration code (e.g. BOM/HSG/TC/12345/2012)"
    )
    address = models.TextField(help_text="Full postal street address")
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Society"
        verbose_name_plural = "Societies"

    def __str__(self):
        return f"{self.name} ({self.registration_number})"


class Building(models.Model):
    """
    Wing or Building block inside the society (e.g., Wing A, Wing B).
    """
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name="buildings")
    name = models.CharField(max_length=50, help_text="e.g. Wing A, Tower 1")
    total_floors = models.PositiveIntegerField(default=7)

    class Meta:
        unique_together = ("society", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class FlatType(models.TextChoices):
    ONE_RK = "1RK", "1 RK"
    ONE_BHK = "1BHK", "1 BHK"
    TWO_BHK = "2BHK", "2 BHK"
    THREE_BHK = "3BHK", "3 BHK"
    SHOP = "SHOP", "Commercial Shop"
    OTHER = "OTHER", "Other"


class Flat(models.Model):
    """
    Individual residential unit or flat inside a building wing.
    """
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="flats")
    flat_number = models.CharField(max_length=20, help_text="e.g. 101, 402, G-1")
    floor = models.PositiveIntegerField(default=1)
    flat_type = models.CharField(max_length=10, choices=FlatType.choices, default=FlatType.TWO_BHK)
    square_feet = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=650.00,
        help_text="Carpet / Super built-up area for dues computation"
    )

    class Meta:
        unique_together = ("building", "flat_number")
        ordering = ["building__name", "floor", "flat_number"]

    @property
    def full_name(self):
        return f"{self.building.name}-{self.flat_number}"

    def get_current_occupant(self):
        profile = self.resident_profiles.filter(is_active=True).first()
        return profile.user if profile else None

    def __str__(self):
        return f"{self.building.name} - Flat {self.flat_number}"


class OccupancyType(models.TextChoices):
    OWNER = "OWNER", "Owner"
    TENANT = "TENANT", "Tenant"


class ResidentProfile(models.Model):
    """
    Mapping between a User and a Flat with tenancy/ownership status.
    Keeps occupancy history clean and normalized.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resident_profiles"
    )
    flat = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
        related_name="resident_profiles"
    )
    occupancy_type = models.CharField(
        max_length=15,
        choices=OccupancyType.choices,
        default=OccupancyType.OWNER
    )
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(null=True, blank=True)
    is_primary_contact = models.BooleanField(
        default=True,
        help_text="Designates the primary recipient for notices and dues"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck when resident vacates the flat"
    )

    class Meta:
        ordering = ["-is_active", "flat__building__name", "flat__flat_number"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.flat.full_name} - {self.occupancy_type})"


class StaffProfile(models.Model):
    """
    Technician / maintenance staff profile detailing specialty and availability.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )
    employee_code = models.CharField(max_length=20, unique=True, help_text="e.g. STF-01")
    specialty = models.CharField(
        max_length=100,
        help_text="e.g. Electrician, Plumber, Lift Technician, Security, Cleaning"
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.specialty} ({self.employee_code})"

