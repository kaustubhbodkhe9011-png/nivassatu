from django import forms
from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "category", "content", "is_pinned", "expires_at"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "Notice Headline"}),
            "category": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "content": forms.Textarea(attrs={"rows": 5, "class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "Enter full announcement text..."}),
            "is_pinned": forms.CheckboxInput(attrs={"class": "rounded text-indigo-600 focus:ring-indigo-500"}),
            "expires_at": forms.DateInput(attrs={"type": "date", "class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
        }

