from django import forms
from .models import Payment, PaymentMode

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "payment_mode", "transaction_reference", "payment_date", "remarks"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "step": "0.01"}),
            "payment_mode": forms.Select(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "transaction_reference": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "UPI UTR / Cheque No"}),
            "payment_date": forms.DateInput(attrs={"type": "date", "class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"}),
            "remarks": forms.TextInput(attrs={"class": "w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800", "placeholder": "Notes (Optional)"}),
        }

