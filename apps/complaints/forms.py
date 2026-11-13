from django import forms
from .models import Complaint, ComplaintComment, ComplaintFeedback
from apps.society.models import StaffProfile

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "title", "description", "priority", "photo"]
        widgets = {
            "category": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "title": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "e.g. Water leaking in master bathroom"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "Provide details so staff can prepare tools..."}),
            "priority": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "photo": forms.FileInput(attrs={"class": "w-full px-3 py-2 text-sm text-slate-500"}),
        }

class AssignStaffForm(forms.Form):
    staff_member = forms.ModelChoiceField(
        queryset=StaffProfile.objects.filter(is_available=True),
        empty_label="-- Select Available Staff / Technician --",
        widget=forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm"})
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm", "placeholder": "Assignment instructions..."})
    )

class ComplaintCommentForm(forms.ModelForm):
    class Meta:
        model = ComplaintComment
        fields = ["comment", "is_internal"]
        widgets = {
            "comment": forms.TextInput(attrs={"class": "flex-1 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm", "placeholder": "Write an update or reply..."}),
            "is_internal": forms.CheckboxInput(attrs={"class": "rounded text-indigo-600 focus:ring-indigo-500"}),
        }

class ComplaintFeedbackForm(forms.ModelForm):
    class Meta:
        model = ComplaintFeedback
        fields = ["rating", "remarks"]
        widgets = {
            "rating": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "remarks": forms.Textarea(attrs={"rows": 3, "class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "How was the service? (Optional)"}),
        }

