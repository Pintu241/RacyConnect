from django import forms
from django.utils import timezone
from .models import PickupRequest
from transactions.models import Transaction

class PickupRequestCreateForm(forms.ModelForm):
    class Meta:
        model = PickupRequest
        fields = [
            'category',
            'estimated_weight',
            'preferred_date',
            'preferred_time_slot',
            'pickup_address',
            'city',
            'postal_code',
            'contact_phone',
            'scrap_image',
            'notes',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'estimated_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g. 25.0'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_time_slot': forms.Select(attrs={'class': 'form-select'}),
            'pickup_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Doorstep address, house/flat #, building'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Active phone number for collector call'}),
            'scrap_image': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional landmarks, access notes, or segregation details'}),
        }

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < timezone.now().date():
            raise forms.ValidationError("Preferred pickup date cannot be in the past.")
        return preferred_date

    def clean_estimated_weight(self):
        weight = self.cleaned_data.get('estimated_weight')
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Estimated weight must be greater than 0 kg.")
        return weight


class PickupCompleteForm(forms.Form):
    actual_weight = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0.1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'id': 'id_actual_weight', 'placeholder': 'e.g. 28.5'}),
        help_text="Actual measured scrap weight in kg"
    )
    agreed_rate_per_kg = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0.5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'id': 'id_agreed_rate', 'placeholder': 'e.g. 14.0'}),
        help_text="Agreed price per kg in ₹"
    )
    payment_method = forms.ChoiceField(
        choices=Transaction.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_payment_method'})
    )
    payment_status = forms.ChoiceField(
        choices=Transaction.PAYMENT_STATUS_CHOICES,
        initial=Transaction.STATUS_PAID,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transaction_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Remarks, cash handed over, or UPI transaction ref'})
    )


class PickupCancelForm(forms.Form):
    cancellation_reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please tell us why you are cancelling this pickup request...'})
    )
