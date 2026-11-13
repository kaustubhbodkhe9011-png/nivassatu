"""
Accounts app models: Custom User with explicit roles (Secretary, Resident, Staff).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    SECRETARY = "SECRETARY", "Secretary / Admin"
    RESIDENT = "RESIDENT", "Resident"
    STAFF = "STAFF", "Staff / Technician"


class User(AbstractUser):
    """
    Custom user model for NivasSetu society management.
    Extends standard Django user with phone number and role classification.
    """
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.RESIDENT,
        help_text="Determines permissions, visible menus, and dashboards.",
        db_index=True,
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Contact phone number (e.g. +91 9876543210)",
    )

    @property
    def is_secretary(self):
        return self.role == UserRole.SECRETARY or self.is_superuser

    @property
    def is_resident(self):
        return self.role == UserRole.RESIDENT

    @property
    def is_staff_member(self):
        return self.role == UserRole.STAFF

    def get_role_badge_class(self):
        badges = {
            UserRole.SECRETARY: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300",
            UserRole.RESIDENT: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
            UserRole.STAFF: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
        }
        return badges.get(self.role, "bg-gray-100 text-gray-800")

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.get_role_display()})" if full else f"{self.username} ({self.get_role_display()})"

