from django import forms
from .models import ScrapCategory

class ScrapCategoryForm(forms.ModelForm):
    class Meta:
        model = ScrapCategory
        fields = ['name', 'description', 'icon', 'base_rate_per_kg', 'min_rate_per_kg', 'max_rate_per_kg', 'unit', 'recyclability_impact', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-recycle, bi-newspaper, etc.'}),
            'base_rate_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50'}),
            'min_rate_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50'}),
            'max_rate_per_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'recyclability_impact': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
