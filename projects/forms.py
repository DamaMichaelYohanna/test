from django import forms
from .models import Project, ProjectAllocation, ProjectLifecycleStage

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'mda', 'project_code', 'project_name', 'lot', 'project_type', 'location', 'category',
            'plain_boq', 'drawing_design', 'award_letter_and_boq',
            'final_companies', 'back_up_companies', 'updated_recommended_companies',
            'technical_status', 'financial_status',
            'budget_amount', 'actual_contract_amount', 'admin_fee',
            'in_house_benchmark', 'cost_percentage',
            'mobilization_received', 'batch_no_mobilization',
            'batch_no_final_payment', 'final_payment_received',
            'staff_assigned', 'current_phase', 'level_of_completion_percentage',
            'project_status', 'payment_status', 'comments', 'remarks'
        ]
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'final_companies': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'back_up_companies': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
            'updated_recommended_companies': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-[#bfa12c] focus:ring-[#bfa12c] py-2 px-3 text-sm'}),
        }

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
