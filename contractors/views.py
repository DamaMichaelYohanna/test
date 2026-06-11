from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, View
from django.db.models import Q  
from django.contrib import messages  
from django.utils import timezone
from django.forms import modelformset_factory   


from .models import Subcontractor, ComplianceRequirement, SubcontractorCompliance
from .forms import SubcontractorForm, ComplianceUpdateForm, ComplianceRequirementForm

class SubcontractorListView(ListView):
    model = Subcontractor
    template_name = 'contractors/list_contractor.html'
    context_object_name = 'subcontractors'
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '').strip()
        type_filter = self.request.GET.get('type', '').strip().upper()
        if type_filter in ['INTERNAL', 'EXTERNAL']:
            queryset = queryset.filter(company_type=type_filter)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(contact_person__icontains=search_query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Subcontractors'
        context['current_search'] = self.request.GET.get('q', '')
        context['current_type'] = self.request.GET.get('type', '')
        return context


def add_subcontractor(request):
    
    if request.method == 'POST':
        form = SubcontractorForm(request.POST)  
        if form.is_valid():
            form.save()
            messages.success(request, f"Subcontractor '{form.cleaned_data['name']}' added successfully.")
        else:
            messages.error(request, form.errors)
        return redirect('contractors:contractor_list')
    form = SubcontractorForm()
    return render(request, 'contractors/add_subcontractor.html', 
                        {'page_title': 'Add Subcontractor', 
                        'form':form })

def edit_subcontractor(request, pk):
    sub = get_object_or_404(Subcontractor, pk=pk)
    
    if request.method == 'POST':
        sub.name = request.POST.get('name', sub.name)
        sub.company_type = request.POST.get('company_type', sub.company_type)
        sub.contact_person = request.POST.get('contact_person', sub.contact_person)
        sub.phone_number = request.POST.get('phone', sub.phone_number)
        sub.email = request.POST.get('email', sub.email)
        sub.save()
        return redirect('contractors:contractor_list')

    context = {
        'page_title': 'Edit Contractor',
        'subcontractor': sub,
    }
    return render(request, 'contractors/edit_subcontractor.html', context)

def delete_subcontractor(request, pk):
    sub = get_object_or_404(Subcontractor, pk=pk)
    sub.delete()  
    messages.success(request, f"Subcontractor '{sub.name}' deleted successfully.")  
    return redirect('contractors:contractor_list')  


class ComplianceMatrixView(TemplateView):
    template_name = 'contractors/compliance_matrix.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Get the target year from the URL query parameters, default to current year
        current_year = timezone.now().year
        selected_year = int(self.request.GET.get('year', current_year))
        
        # 2. Fetch all active requirements and subcontractors
        requirements = ComplianceRequirement.objects.all()
        subcontractors = Subcontractor.objects.all()
        
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            subcontractors = subcontractors.filter(name__icontains=search_query)
        
        # 3. Pull all compliance records for the target year in ONE optimized database hit
        compliance_records = SubcontractorCompliance.objects.filter(year=selected_year).select_related(
            'subcontractor', 'requirement'
        )
        
        # 4. Build a lookup dictionary: {(subcontractor_id, requirement_id): record_status_or_object}
        # This acts as our fast-access database cache in memory
        lookup_matrix = {
            (record.subcontractor_id, record.requirement_id): record 
            for record in compliance_records
        }
        
        # 5. Restructure the data into a clean grid dictionary for easy template looping
        matrix_data = []
        for contractor in subcontractors:
            contractor_row = {
                'contractor': contractor,
                'requirements': [],
                'fully_compliant': True  # Assume true until proven otherwise
            }
            
            for req in requirements:
                record = lookup_matrix.get((contractor.id, req.id))
                
                # Evaluate compliance status for the row
                status = record.status if record else 'PENDING'
                is_valid = status in ['APPROVED', 'SUBMITTED']
                
                if req.is_mandatory and not is_valid:
                    contractor_row['fully_compliant'] = False
                
                contractor_row['requirements'].append({
                    'requirement': req,
                    'record': record,
                    'status': status
                })
                
            matrix_data.append(contractor_row)
            
        # 6. Populate Context variables for the HTML template
        context['page_title'] = f'Annual Compliance Matrix ({selected_year})'
        context['selected_year'] = selected_year
        # Generate a list of years for a year-picker dropdown menu (e.g., past 3 years to next year)
        context['year_range'] = range(current_year - 3, current_year + 2)
        context['requirements'] = requirements
        context['matrix_data'] = matrix_data
        context['current_search'] = search_query
        
        return context

class ManageComplianceView(View):
    template_name = 'contractors/manage_compliance.html'

    def get_matrix_data(self, selected_year):
        """Helper to safely initialize and pull compliance pairs."""
        subcontractors = Subcontractor.objects.all()
        requirements = ComplianceRequirement.objects.all()
        
        # Auto-provision missing rows safely
        for contractor in subcontractors:
            for req in requirements:
                SubcontractorCompliance.objects.get_or_create(
                    subcontractor=contractor,
                    requirement=req,
                    year=selected_year,
                    defaults={'status': 'PENDING'}
                )
                
        # Return the ordered records to bind to our Formset
        return SubcontractorCompliance.objects.filter(year=selected_year).select_related('subcontractor', 'requirement')

    def get(self, request, *args, **kwargs):
        current_year = timezone.now().year
        selected_year = int(request.GET.get('year', current_year))
        
        queryset = self.get_matrix_data(selected_year)
        
        # Build the formset container (no pagination needed here, we want the full grid)
        ComplianceFormSet = modelformset_factory(SubcontractorCompliance, form=ComplianceUpdateForm, extra=0)
        formset = ComplianceFormSet(queryset=queryset)
        
        # Zip forms and records together so we can arrange them neatly as a grid table in HTML
        forms_and_records = zip(formset, queryset)
        
        context = {
            'page_title': f'Manage Annual Compliance ({selected_year})',
            'formset': formset,
            'forms_and_records': forms_and_records,
            'selected_year': selected_year,
            'year_range': range(current_year - 2, current_year + 2),
            'requirements': ComplianceRequirement.objects.all(),
            'subcontractors': Subcontractor.objects.all(),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_year = int(request.GET.get('year', timezone.now().year))
        
        ComplianceFormSet = modelformset_factory(SubcontractorCompliance, form=ComplianceUpdateForm, extra=0)
        formset = ComplianceFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            # Redirect back to the read-only matrix overview page we created earlier
            return redirect('contractors:compliance_matrix')
            
        # If errors happen, reload screen with state
        queryset = SubcontractorCompliance.objects.filter(year=selected_year).select_related('subcontractor', 'requirement')
        context = {
            'page_title': f'Manage Annual Compliance ({selected_year})',
            'formset': formset,
            'forms_and_records': zip(formset, queryset),
            'selected_year': selected_year,
            'year_range': range(timezone.now().year - 2, timezone.now().year + 2),
            'requirements': ComplianceRequirement.objects.all(),
        }
        return render(request, self.template_name, context)

def manage_compliance_requirements(request):
    edit_id = request.GET.get('edit')
    req_instance = None
    if edit_id:
        req_instance = get_object_or_404(ComplianceRequirement, pk=edit_id)
        
    if request.method == 'POST':
        form = ComplianceRequirementForm(request.POST, instance=req_instance)
        if form.is_valid():
            form.save()
            if req_instance:
                messages.success(request, "Compliance requirement updated successfully.")
            else:
                messages.success(request, "New compliance requirement added successfully.")
            return redirect('contractors:manage_compliance_requirements')
    else:
        form = ComplianceRequirementForm(instance=req_instance)
    
    requirements = ComplianceRequirement.objects.all()
    context = {
        'page_title': 'Manage Compliance Requirements',
        'requirements': requirements,
        'form': form,
        'is_editing': req_instance is not None,
        'edit_instance': req_instance,
    }
    return render(request, 'contractors/manage_requirements.html', context)