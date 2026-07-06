from django import forms
from django.forms import inlineformset_factory
from .models import (
    Project, ProjectCategory, ProjectAllocation, ProjectLifecycleStage, 
    ProjectFee, FeeType, ProjectMonitoringLog, ProjectMonitoringImage
)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'project_code', 'mda', 'project_name', 'project_type', 'execution_mode', 'lot', 'location', 'category', 'linked_project',
            'budget_amount', 'technical_status', 'financial_status', 'final_companies', 'back_up_companies', 'updated_recommended_companies',
            'plain_boq', 'drawing_design',
            'actual_contract_amount', 'in_house_benchmark', 'cost_percentage', 'staff_assigned', 'current_phase',
            'mobilization_received', 'batch_no_mobilization', 'final_payment_received', 'batch_no_final_payment',
            'award_letter_and_boq',
            'execution_level_percentage', 'project_status', 'payment_status', 'comments', 'remarks'
        ]
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'final_companies': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'back_up_companies': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'updated_recommended_companies': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['linked_project'].queryset = Project.objects.exclude(pk=self.instance.pk)
        
        # Style form fields using modern Tailwind classes
        for name, field in self.fields.items():
            if name not in ['comments', 'remarks', 'final_companies', 'back_up_companies', 'updated_recommended_companies', 'plain_boq', 'drawing_design', 'award_letter_and_boq']:
                field.widget.attrs.setdefault('class', 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm')


ProjectFeeFormSet = inlineformset_factory(
    Project,
    ProjectFee,
    fields=('fee_type', 'amount'),
    extra=1,
    can_delete=True,
    widgets={
        'fee_type': forms.Select(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
        'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
    }
)

class ProjectAllocationForm(forms.ModelForm):
    class Meta:
        model = ProjectAllocation
        fields = [
            'subcontractor', 'sub_contractor_drawing_design', 'supplier_contractor_price_boq',
            'sub_contractor_cost_percentage', 'amount_agreed_with_supplier_contractor',
            'advance_received_by_supplier_contractor'
        ]

class ProjectLifecycleStageForm(forms.ModelForm):
    class Meta:
        model = ProjectLifecycleStage
        fields = ['is_completed', 'completed_date', 'notes_or_updates', 'incurred_cost']
        widgets = {
            'completed_date': forms.DateInput(attrs={'type': 'date'}),
            'notes_or_updates': forms.Textarea(attrs={'rows': 2}),
        }


class ProjectCategoryForm(forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
        }


class FeeTypeForm(forms.ModelForm):
    class Meta:
        model = FeeType
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
        }


class ProjectMonitoringLogForm(forms.ModelForm):
    class Meta:
        model = ProjectMonitoringLog
        fields = ['start_date', 'end_date', 'reported_execution_percentage', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'reported_execution_percentage': forms.NumberInput(attrs={'min': 0, 'max': 100, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm', 'placeholder': 'Provide a detailed description of what is happening on site...'}),
        }


class ProjectMonitoringLogGlobalForm(ProjectMonitoringLogForm):
    class Meta(ProjectMonitoringLogForm.Meta):
        fields = ['project'] + ProjectMonitoringLogForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].widget.attrs.update({'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'})
        self.fields['project'].queryset = Project.objects.all()


