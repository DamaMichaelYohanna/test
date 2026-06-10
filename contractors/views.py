from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.db.models import Q  
from django.contrib import messages  


from .models import Subcontractor
from .forms import SubcontractorForm

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
        return redirect('contractor_list')

    context = {
        'page_title': 'Edit Contractor',
        'subcontractor': sub,
    }
    return render(request, 'contractors/edit_subcontractor.html', context)

def delete_subcontractor(request, pk):
    sub = get_object_or_404(Subcontractor, pk=pk)
    sub.is_active = False
    sub.save()  
    messages.success(request, f"Subcontractor '{sub.name}' deleted successfully.")  
    return redirect('contractor_list')  