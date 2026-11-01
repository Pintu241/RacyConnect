from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import CollectorProfile, RecyclerProfile

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        min_length=6
    )
    role = forms.ChoiceField(
        choices=[
            (User.ROLE_CUSTOMER, 'Household / Business Customer (Sell Scrap)'),
            (User.ROLE_COLLECTOR, 'Scrap Collector (Collect & Earn)'),
            (User.ROLE_RECYCLER, 'Recycling Company (Procure Bulk Materials)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select your primary role in RecyConnect"
    )

    # Collector fields (optional at registration)
    service_area = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Green City Downtown, East Sector'})
    )
    vehicle_type = forms.ChoiceField(
        choices=CollectorProfile.VEHICLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Recycler fields (optional at registration)
    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registered company or plant name'})
    )
    license_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pollution Control / Trade License'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'address', 'city', 'postal_code']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address, apartment/flat'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN / Postal Code'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        role = cleaned_data.get('role')
        if role == User.ROLE_RECYCLER and not cleaned_data.get('company_name'):
            cleaned_data['company_name'] = f"{cleaned_data.get('first_name', '')} Recycling"

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Post-save handles profile creation, now update specific fields:
            if user.role == User.ROLE_COLLECTOR:
                profile = user.collector_profile
                if self.cleaned_data.get('service_area'):
                    profile.service_area = self.cleaned_data['service_area']
                if self.cleaned_data.get('vehicle_type'):
                    profile.vehicle_type = self.cleaned_data['vehicle_type']
                profile.save()
            elif user.role == User.ROLE_RECYCLER:
                profile = user.recycler_profile
                if self.cleaned_data.get('company_name'):
                    profile.company_name = self.cleaned_data['company_name']
                if self.cleaned_data.get('license_number'):
                    profile.license_number = self.cleaned_data['license_number']
                profile.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'city', 'state', 'postal_code', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CollectorProfileForm(forms.ModelForm):
    class Meta:
        model = CollectorProfile
        fields = ['service_area', 'vehicle_type', 'id_proof_type', 'id_proof_number', 'id_proof_document', 'is_available']
        widgets = {
            'service_area': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'id_proof_type': forms.TextInput(attrs={'class': 'form-control'}),
            'id_proof_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_proof_document': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RecyclerProfileForm(forms.ModelForm):
    class Meta:
        model = RecyclerProfile
        fields = ['company_name', 'license_number', 'gst_number', 'facility_address', 'processing_capacity_tons', 'materials_accepted']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'facility_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'processing_capacity_tons': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'materials_accepted': forms.TextInput(attrs={'class': 'form-control'}),
        }
