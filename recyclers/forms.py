from django import forms
from .models import PurchaseRequest
from scrap.models import ScrapCategory

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = [
            'category',
            'requested_quantity_kg',
            'offered_price_per_kg',
            'delivery_facility_address',
            'special_specifications',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'requested_quantity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '50', 'placeholder': 'e.g. 1000 kg'}),
            'offered_price_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g. 18.00'}),
            'delivery_facility_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Processing plant, warehouse dock or factory address'}),
            'special_specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g., Sorted HDPE only, moisture under 10%, baled'}),
        }

    def clean_requested_quantity_kg(self):
        qty = self.cleaned_data.get('requested_quantity_kg')
        if qty is not None and qty <= 0:
            raise forms.ValidationError("Quantity must be greater than 0 kg.")
        return qty

    def clean_offered_price_per_kg(self):
        price = self.cleaned_data.get('offered_price_per_kg')
        if price is not None and price <= 0:
            raise forms.ValidationError("Offered price per kg must be greater than 0.")
        return price
