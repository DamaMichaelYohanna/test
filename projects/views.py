from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.db.models import Q

from .models import Project, ProjectAllocation, ProjectLifecycleStage
from .forms import ProjectForm, ProjectAllocationForm, ProjectLifecycleStageForm

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

    def form_valid(self, form):
        messages.success(self.request, "Project created successfully!")
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Project updated successfully!")
        return super().form_valid(form)

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
        # Fetch subcontractor allocations
        context['allocations'] = ProjectAllocation.objects.filter(project=self.object).select_related('subcontractor')
        # Fetch lifecycle stages ordered by sequence_order
        context['lifecycle_stages'] = self.object.lifecycle_stages.all()
        # Form for adding allocation in modal/page
        context['allocation_form'] = ProjectAllocationForm()
        # Calculate totals
        total_incurred_cost = sum(stage.incurred_cost for stage in context['lifecycle_stages'])
        context['total_incurred_cost'] = total_incurred_cost
        
        # Calculate completion percentage based on completed stages vs total stages
        total_stages = context['lifecycle_stages'].count()
        completed_stages = context['lifecycle_stages'].filter(is_completed=True).count()
        if total_stages > 0:
            context['calculated_completion_percentage'] = int((completed_stages / total_stages) * 100)
        else:
            context['calculated_completion_percentage'] = 0
            
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
