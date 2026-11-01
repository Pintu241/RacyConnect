from django import forms
from .models import ContactMessage, Complaint

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number (optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of your inquiry'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'How can we help you?'}),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['pickup', 'subject', 'description']
        widgets = {
            'pickup': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description of issue'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide details about what went wrong...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from pickups.models import PickupRequest
            self.fields['pickup'].queryset = PickupRequest.objects.filter(customer=user)
            self.fields['pickup'].required = False
