from django import forms
from django.forms.widgets import TextInput, Select, EmailInput
from .models import Subcontractor, SubcontractorCompliance, ComplianceRequirement

class SubcontractorForm(forms.ModelForm):
    class Meta:
        model = Subcontractor
        fields = ['name', 'company_type', 'contact_person', 'phone_number', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcontractor Name'})
        self.fields['company_type'].widget = Select(attrs={'class': 'form-control', 'placeholder': 'Company Type'})
        self.fields['contact_person'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'})
        self.fields['phone_number'].widget = TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
        self.fields['email'].widget = EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})

class ComplianceUpdateForm(forms.ModelForm):
    class Meta:
        model = SubcontractorCompliance
        fields = ['status', 'expiry_date']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 rounded text-gray-950 text-xs p-1 focus:outline-none focus:ring-1 focus:ring-[#bfa12c]'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'bg-gray-50 border border-gray-300 rounded text-gray-950 text-xs p-1 w-28 focus:outline-none focus:ring-1 focus:ring-[#bfa12c]'
            }),
        }

class ComplianceRequirementForm(forms.ModelForm):
    class Meta:
        model = ComplianceRequirement
        fields = ['name', 'description', 'is_mandatory']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#bfa12c] focus:border-[#bfa12c] text-sm text-gray-900 transition duration-150',
                'placeholder': 'Requirement Name (e.g. COREN Audit)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#bfa12c] focus:border-[#bfa12c] text-sm text-gray-900 transition duration-150',
                'rows': 3,
                'placeholder': 'Brief details about document requirements...'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-[#bfa12c] focus:ring-[#bfa12c] h-4 w-4 transition duration-150'
            }),
        }