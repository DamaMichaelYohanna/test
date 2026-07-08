from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.db.models import Q

from .models import (
    Project, ProjectCategory, ProjectAllocation, ProjectLifecycleStage, 
    ProjectFee, FeeType, ProjectMonitoringLog, ProjectMonitoringImage,
    SubcontractorPaymentTranche
)
from .forms import (
    ProjectForm, ProjectAllocationForm, ProjectLifecycleStageForm, 
    ProjectFeeFormSet, ProjectCategoryForm, FeeTypeForm, ProjectMonitoringLogForm,
    ProjectMonitoringLogGlobalForm, SubcontractorPaymentTrancheForm
)

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        year = self.request.GET.get('year', '').strip()
        mda = self.request.GET.get('mda', '').strip()
        project_type = self.request.GET.get('project_type', '').strip()

        if q:
            qs = qs.filter(
                Q(project_code__icontains=q) | Q(project_name__icontains=q)
            )
        if year:
            qs = qs.filter(created_at__year=year)
        if mda:
            qs = qs.filter(mda__icontains=mda)
        if project_type:
            qs = qs.filter(project_type=project_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass current filter values back so the form stays populated
        context['q'] = self.request.GET.get('q', '')
        context['selected_year'] = self.request.GET.get('year', '')
        context['selected_mda'] = self.request.GET.get('mda', '')
        context['selected_type'] = self.request.GET.get('project_type', '')
        # Build distinct filter option lists from the full table
        context['year_choices'] = (
            Project.objects.dates('created_at', 'year', order='DESC')
        )
        context['mda_choices'] = (
            Project.objects.values_list('mda', flat=True).distinct().order_by('mda')
        )
        context['type_choices'] = Project.PROJECT_TYPE_CHOICES
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['fee_formset'] = ProjectFeeFormSet(self.request.POST)
        else:
            data['fee_formset'] = ProjectFeeFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fee_formset = context['fee_formset']
        if fee_formset.is_valid():
            self.object = form.save()
            fee_formset.instance = self.object
            fee_formset.save()
            messages.success(self.request, "Project created successfully!")
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['fee_formset'] = ProjectFeeFormSet(self.request.POST, instance=self.object)
        else:
            data['fee_formset'] = ProjectFeeFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fee_formset = context['fee_formset']
        if fee_formset.is_valid():
            self.object = form.save()
            fee_formset.instance = self.object
            fee_formset.save()
            messages.success(self.request, "Project updated successfully!")
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch subcontractor allocations with prefetched tranches
        context['allocations'] = ProjectAllocation.objects.filter(project=self.object).select_related('subcontractor').prefetch_related('payment_tranches')
        context['tranche_form'] = SubcontractorPaymentTrancheForm()
        # Fetch lifecycle stages ordered by sequence_order
        lifecycle_stages = self.object.lifecycle_stages.all()
        context['lifecycle_stages'] = lifecycle_stages
        
        # Group lifecycle stages by phases
        phase1 = []
        phase2 = []
        phase3 = []
        
        # Thresholds based on project type (from signals.py logic)
        if self.object.project_type == 'CONSTRUCTION':
            phase2_limit = 25
        else:
            phase2_limit = 19
            
        for stage in lifecycle_stages:
            if stage.sequence_order <= 17:
                phase1.append(stage)
            elif stage.sequence_order <= phase2_limit:
                phase2.append(stage)
            else:
                phase3.append(stage)
                
        context['phase1_stages'] = phase1
        context['phase2_stages'] = phase2
        context['phase3_stages'] = phase3

        # Form for adding allocation in modal/page
        context['allocation_form'] = ProjectAllocationForm()
        # Calculate totals
        total_incurred_cost = sum(stage.incurred_cost for stage in lifecycle_stages)
        context['total_incurred_cost'] = total_incurred_cost
        
        # Fetch completion percentage based on completed stages vs total stages
        total_stages = context['lifecycle_stages'].count()
        completed_stages = context['lifecycle_stages'].filter(is_completed=True).count()
        if total_stages > 0:
            context['calculated_completion_percentage'] = int((completed_stages / total_stages) * 100)
        else:
            context['calculated_completion_percentage'] = 0
            
        # Fetch site monitoring logs and their images
        context['monitoring_logs'] = self.object.monitoring_logs.all().prefetch_related('images')
        context['monitoring_form'] = ProjectMonitoringLogForm()
        return context

class ProjectAllocationCreateView(LoginRequiredMixin, View):
    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        form = ProjectAllocationForm(request.POST, request.FILES)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.project = project
            try:
                allocation.save()
                messages.success(request, "Subcontractor allocated successfully!")
            except Exception as e:
                messages.error(request, f"Failed to allocate subcontractor: {e}")
        else:
            messages.error(request, "Invalid form submission.")
        return redirect('projects:project_detail', pk=project.pk)

class ProjectAllocationUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectAllocation
    form_class = ProjectAllocationForm
    template_name = 'projects/allocation_form.html'

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})

    def form_valid(self, form):
        messages.success(self.request, "Allocation updated successfully!")
        return super().form_valid(form)

class ProjectAllocationDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectAllocation
    template_name = 'confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})

class UpdateLifecycleStageView(LoginRequiredMixin, View):
    def post(self, request, pk):
        stage = get_object_or_404(ProjectLifecycleStage, pk=pk)
        is_completed = request.POST.get('is_completed') == 'true'
        notes = request.POST.get('notes_or_updates', '')
        incurred_cost = request.POST.get('incurred_cost', '0.00')

        stage.is_completed = is_completed
        stage.notes_or_updates = notes
        try:
            stage.incurred_cost = float(incurred_cost)
        except ValueError:
            pass

        if is_completed and not stage.completed_date:
            stage.completed_date = now().date()
        elif not is_completed:
            stage.completed_date = None

        stage.save()
        messages.success(request, f"Updated step: {stage.stage_name}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class ProjectSettingsView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "Access denied. Admins only.")
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, request, cat_form=None, fee_form=None, active_tab='categories'):
        edit_cat_id = request.GET.get('edit_cat')
        edit_fee_id = request.GET.get('edit_fee')
        
        if cat_form is None:
            cat_instance = get_object_or_404(ProjectCategory, pk=edit_cat_id) if edit_cat_id else None
            cat_form = ProjectCategoryForm(instance=cat_instance)
            
        if fee_form is None:
            fee_instance = get_object_or_404(FeeType, pk=edit_fee_id) if edit_fee_id else None
            fee_form = FeeTypeForm(instance=fee_instance)
            
        return {
            'categories': ProjectCategory.objects.all(),
            'fee_types': FeeType.objects.all(),
            'cat_form': cat_form,
            'fee_form': fee_form,
            'is_editing_cat': edit_cat_id is not None,
            'is_editing_fee': edit_fee_id is not None,
            'edit_cat_id': edit_cat_id,
            'edit_fee_id': edit_fee_id,
            'active_tab': active_tab,
        }

    def get(self, request):
        edit_fee_id = request.GET.get('edit_fee')
        active_tab = 'feetypes' if edit_fee_id else 'categories'
        return render(request, 'projects/settings.html', self.get_context_data(request, active_tab=active_tab))

    def post(self, request):
        action = request.POST.get('action')
        if action == 'save_category':
            edit_cat_id = request.GET.get('edit_cat')
            cat_instance = get_object_or_404(ProjectCategory, pk=edit_cat_id) if edit_cat_id else None
            form = ProjectCategoryForm(request.POST, instance=cat_instance)
            if form.is_valid():
                form.save()
                messages.success(request, "Project category saved successfully.")
                return redirect('projects:settings')
            else:
                messages.error(request, "Failed to save category. Please correct the errors.")
                context = self.get_context_data(request, cat_form=form, active_tab='categories')
                return render(request, 'projects/settings.html', context)
                
        elif action == 'save_feetype':
            edit_fee_id = request.GET.get('edit_fee')
            fee_instance = get_object_or_404(FeeType, pk=edit_fee_id) if edit_fee_id else None
            form = FeeTypeForm(request.POST, instance=fee_instance)
            if form.is_valid():
                form.save()
                messages.success(request, "Fee type saved successfully.")
                return redirect('projects:settings')
            else:
                messages.error(request, "Failed to save fee type. Please correct the errors.")
                context = self.get_context_data(request, fee_form=form, active_tab='feetypes')
                return render(request, 'projects/settings.html', context)

        elif action == 'delete_category':
            cat_id = request.POST.get('cat_id')
            category = get_object_or_404(ProjectCategory, pk=cat_id)
            if category.project_set.exists():
                messages.error(request, f"Cannot delete category '{category.name}' because it is assigned to projects.")
            else:
                category.delete()
                messages.success(request, "Category deleted successfully.")
            return redirect('projects:settings')

        elif action == 'delete_feetype':
            fee_id = request.POST.get('fee_id')
            feetype = get_object_or_404(FeeType, pk=fee_id)
            if feetype.projectfee_set.exists():
                messages.error(request, f"Cannot delete fee type '{feetype.name}' because it is assigned to projects.")
            else:
                feetype.delete()
                messages.success(request, "Fee type deleted successfully.")
            return redirect('projects:settings')


class ProjectMonitoringLogCreateView(LoginRequiredMixin, View):
    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        form = ProjectMonitoringLogForm(request.POST)
        if form.is_valid():
            log_entry = form.save(commit=False)
            log_entry.project = project
            log_entry.reported_by = request.user
            log_entry.save()
            
            # Handle multiple images
            images = request.FILES.getlist('images')
            for img in images:
                ProjectMonitoringImage.objects.create(
                    monitoring_log=log_entry,
                    image=img
                )
            messages.success(request, f"Monitoring log updated. Project progress set to {log_entry.reported_execution_percentage}%.")
        else:
            messages.error(request, "Error creating monitoring log. Please verify details.")
        return redirect('projects:project_detail', pk=project.pk)


class ProjectMonitoringDashboardView(LoginRequiredMixin, View):
    template_name = 'projects/monitoring_dashboard.html'

    def get(self, request):
        project_id = request.GET.get('project')
        logs_qs = ProjectMonitoringLog.objects.all().prefetch_related('images').select_related('project', 'reported_by')
        selected_project = None
        if project_id and project_id != '0':
            logs_qs = logs_qs.filter(project_id=project_id)
            selected_project = get_object_or_404(Project, pk=project_id)

        context = {
            'logs': logs_qs.order_by('-reported_at'),
            'projects': Project.objects.all(),
            'selected_project': selected_project,
            'monitoring_form': ProjectMonitoringLogGlobalForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = ProjectMonitoringLogGlobalForm(request.POST, request.FILES)
        if form.is_valid():
            log_entry = form.save(commit=False)
            log_entry.reported_by = request.user
            log_entry.save()
            
            # Handle multiple images
            images = request.FILES.getlist('images')
            for img in images:
                ProjectMonitoringImage.objects.create(
                    monitoring_log=log_entry,
                    image=img
                )
            messages.success(request, f"Monitoring log submitted for project {log_entry.project.project_code}. Progress updated to {log_entry.reported_execution_percentage}%.")
        else:
            messages.error(request, "Failed to submit monitoring log. Please correct form errors.")
        return redirect('projects:monitoring_dashboard')


class SubcontractorPaymentTrancheCreateView(LoginRequiredMixin, View):
    def post(self, request, allocation_pk):
        allocation = get_object_or_404(ProjectAllocation, pk=allocation_pk)
        form = SubcontractorPaymentTrancheForm(request.POST)
        if form.is_valid():
            tranche = form.save(commit=False)
            tranche.allocation = allocation
            tranche.save()
            messages.success(request, f"Recorded payment tranche of ₦{tranche.amount:,.2f} for {allocation.subcontractor.name} successfully!")
        else:
            messages.error(request, "Failed to record payment tranche. Please check form values.")
        return redirect('projects:project_detail', pk=allocation.project.pk)


