from django.forms import ModelForm, TextInput, Select, EmailInput
from .models import Subcontractor   
class SubcontractorForm(ModelForm):
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
