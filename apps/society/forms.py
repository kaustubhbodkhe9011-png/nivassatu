from django import forms
from .models import Flat, ResidentProfile, Building

class FlatForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = ["building", "flat_number", "floor", "flat_type", "square_feet"]
        widgets = {
            "building": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "flat_number": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "e.g. 101"}),
            "floor": forms.NumberInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "flat_type": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "square_feet": forms.NumberInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
        }

class AssignResidentForm(forms.ModelForm):
    class Meta:
        model = ResidentProfile
        fields = ["user", "flat", "occupancy_type", "move_in_date", "is_primary_contact", "is_active"]
        widgets = {
            "user": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "flat": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "occupancy_type": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "move_in_date": forms.DateInput(attrs={"type": "date", "class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
        }

