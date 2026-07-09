from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.db.models import Sum
from projects.models import Project
from .models import SiteStore, MilestoneCashRequest, SiteUsageLog
from core.permissions import Level2RequiredMixin, Level3RequiredMixin, Level4RequiredMixin
from django.views import View


class SiteLogisticsLandingView(LoginRequiredMixin, ListView):
    """
    Landing page for site logistics when no project is explicitly selected.
    Allows the user to select a project to jump into its logistics hub.
    """
    model = Project
    template_name = 'logistics/landing.html'
    context_object_name = 'projects'


class ProjectLogisticsDashboardView(LoginRequiredMixin, ListView):
    """
    Main hub for a specific site. Displays local stock inventory levels,
    historical cash requests, and recent material usage logs.
    """
    model = SiteStore
    template_name = 'logistics/project_hub.html'
    context_object_name = 'inventory_items'

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        if project.execution_mode == 'SUBCONTRACTED':
            messages.warning(request, f"Logistics & material tracking are disabled for subcontracted project '{project.project_code}'.")
            return redirect('projects:project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return SiteStore.objects.filter(project=self.project)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['page_title'] = f"Logistics Hub: {self.project.project_name}"
        context['pending_request_count'] = MilestoneCashRequest.objects.filter(
            project=self.project, status='PENDING'
        ).count()   
        context['cash_requests'] = MilestoneCashRequest.objects.filter(
            project=self.project
        ).select_related('requested_by').order_by('-date_requested')
        context['recent_usage'] = SiteUsageLog.objects.filter(
            site_store__project=self.project
        ).select_related('site_store').order_by('-date_used')[:10]
        return context


class AddSiteStoreInventoryView(Level2RequiredMixin, View):
    """
    Handles adding a new material line or restocking an existing one.
    Uses get_or_create so engineers can keep adding to the same material
    without creating duplicates.
    """
    template_name = 'logistics/add_inventory_form.html'

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        if project.execution_mode == 'SUBCONTRACTED':
            messages.warning(request, "Logistics and material tracking are disabled for Subcontracted projects.")
            return redirect('projects:project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, project_id):
        from django import forms as django_forms

        project = get_object_or_404(Project, pk=project_id)
        # Pass existing inventory items for a quick restock dropdown helper
        existing_items = SiteStore.objects.filter(project=project)
        return _render_inventory_form(request, project, existing_items)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        material_name = request.POST.get('material_name', '').strip()
        unit = request.POST.get('unit_of_measurement', '').strip()
        qty_str = request.POST.get('quantity_to_add', '0').strip()

        if not material_name or not unit:
            messages.error(request, "Material name and unit of measurement are required.")
            return redirect('logistic:project_logistics_hub', project_id=project_id)

        try:
            quantity = float(qty_str)
        except ValueError:
            messages.error(request, "Please enter a valid quantity number.")
            return redirect('logistic:project_logistics_hub', project_id=project_id)

        # Either create a new stock line or top up the existing one
        store_item, created = SiteStore.objects.get_or_create(
            project=project,
            material_name=material_name,
            defaults={'unit_of_measurement': unit, 'quantity_on_site': quantity}
        )
        if not created:
            store_item.quantity_on_site += quantity
            store_item.unit_of_measurement = unit  # allow unit correction on restock
            store_item.save()
            messages.success(request, f"Restocked {quantity} {unit} of {material_name}. "
                                      f"New total: {store_item.quantity_on_site} {unit}.")
        else:
            messages.success(request, f"{material_name} added to site store ({quantity} {unit}).")

        return redirect('logistic:project_logistics_hub', project_id=project_id)


def _render_inventory_form(request, project, existing_items):
    """Helper to render the inventory form with context."""
    from django.shortcuts import render
    return render(request, 'logistics/add_inventory_form.html', {
        'project': project,
        'existing_items': existing_items,
        'page_title': f"Add / Restock Material — {project.project_name}",
    })


class MilestoneCashRequestCreateView(Level2RequiredMixin, CreateView):
    """
    Handles Civil Engineers submitting field tranches linked to specific milestones.
    """
    model = MilestoneCashRequest
    fields = ['milestone_title', 'amount_requested', 'justification_notes']
    template_name = 'logistics/cash_request_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determine project either from URL kwarg or POST data (dashboard form)
        project_id = self.kwargs.get('project_id') or self.request.POST.get('project_id')
        context['project'] = get_object_or_404(Project, pk=project_id)
        context['page_title'] = "Submit Milestone Cash Request"
        return context

    def form_valid(self, form):
        # Retrieve project ID from URL or POST payload
        project_id = self.kwargs.get('project_id') or self.request.POST.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        form.instance.project = project
        form.instance.requested_by = self.request.user
        form.instance.status = 'PENDING'
        messages.success(self.request, "Cash request submitted successfully. Pending management review.")
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect back to the project hub if we know the project, otherwise fallback to dashboard
        project_id = self.kwargs.get('project_id') or self.request.POST.get('project_id')
        if project_id:
            return reverse_lazy('logistic:project_logistics_hub', kwargs={'project_id': project_id})
        return reverse_lazy('logistic:cash_requests_dashboard')


class LogSiteUsageCreateView(Level2RequiredMixin, CreateView):
    """
    Records material consumption on site and subtracts from local stock.
    """
    model = SiteUsageLog
    fields = ['site_store', 'quantity_used', 'date_used', 'activity_details']
    template_name = 'logistics/usage_form.html'

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        if project.execution_mode == 'SUBCONTRACTED':
            messages.warning(request, "Logistics and material tracking are disabled for Subcontracted projects.")
            return redirect('projects:project_detail', pk=project.pk)
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_id'])
        context['page_title'] = "Log Site Material Usage"
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Limit site_store choices to only materials at THIS site
        form.fields['site_store'].queryset = SiteStore.objects.filter(
            project_id=self.kwargs['project_id']
        )
        return form

    def form_valid(self, form):
        usage_record = form.instance
        site_stock = usage_record.site_store

        # Guard against going negative
        if usage_record.quantity_used > site_stock.quantity_on_site:
            form.add_error('quantity_used',
                           f"Cannot log {usage_record.quantity_used} — only "
                           f"{site_stock.quantity_on_site} {site_stock.unit_of_measurement} on site.")
            return self.form_invalid(form)

        response = super().form_valid(form)
        site_stock.quantity_on_site -= usage_record.quantity_used
        site_stock.save()
        messages.success(self.request,
                         f"Usage logged. {site_stock.material_name} stock updated to "
                         f"{site_stock.quantity_on_site} {site_stock.unit_of_measurement}.")
        return response

    def get_success_url(self):
        return reverse_lazy('logistic:project_logistics_hub', kwargs={'project_id': self.kwargs['project_id']})


class ProcessCashRequestView(Level3RequiredMixin, View):
    """
    Approves or rejects a pending milestone cash request.
    Restricted to Executive / Management group members (Level 3/4) and superusers.
    """

    def post(self, request, request_id):
        cash_request = get_object_or_404(MilestoneCashRequest, pk=request_id)
        action = request.POST.get('action')
        management_comment = request.POST.get('management_comment', '').strip()

        if cash_request.status != 'PENDING':
            messages.error(request, "This request has already been processed.")
            return redirect('logistic:project_logistics_hub', project_id=cash_request.project.pk)

        if action == 'APPROVE':
            cash_request.status = 'APPROVED'
            messages.success(request,
                             f"₦{cash_request.amount_requested:,} tranche approved for "
                             f"'{cash_request.milestone_title}'.")
        elif action == 'REJECT':
            cash_request.status = 'REJECTED'
            messages.warning(request,
                             f"₦{cash_request.amount_requested:,} tranche rejected for "
                             f"'{cash_request.milestone_title}'.")
        elif action == 'CANCEL':
            cash_request.status = 'CANCELLED'
            messages.warning(request,
                             f"₦{cash_request.amount_requested:,} tranche cancelled for "
                             f"'{cash_request.milestone_title}'.")
        else:
            messages.error(request, "Invalid action submitted.")
            return redirect('logistic:project_logistics_hub', project_id=cash_request.project.pk)

        cash_request.date_actioned = timezone.now()
        if management_comment:
            cash_request.management_comment = management_comment
        cash_request.save()
        
        next_url = request.POST.get('next')
        if not next_url and 'cash-requests' in request.META.get('HTTP_REFERER', ''):
            next_url = reverse_lazy('logistic:cash_requests_dashboard')
        if not next_url:
            next_url = reverse_lazy('logistic:project_logistics_hub', kwargs={'project_id': cash_request.project.pk})
        return redirect(next_url)


class CashRequestDashboardView(LoginRequiredMixin, View):
    """Centralised cash request page.

    * Staff (no Level 3/4) – select a project, submit a request, view own requests.
    * Managers (Level 3/4 group or superuser) – see global total, per‑project totals,
      pending requests and list of all requests.
    """
    template_name = 'logistics/cash_requests.html'

    def get(self, request):
        is_manager = request.user.is_superuser or request.user.groups.filter(name__in=['Level 3', 'Level 4']).exists()
        project_id = request.GET.get('project')

        approved_qs = MilestoneCashRequest.objects.filter(status='APPROVED').select_related('project')
        pending_qs = MilestoneCashRequest.objects.filter(status='PENDING').select_related('project', 'requested_by')
        all_qs = MilestoneCashRequest.objects.all().select_related('project', 'requested_by')
        user_qs = MilestoneCashRequest.objects.filter(requested_by=request.user).select_related('project')

        project_obj = None
        if project_id and project_id != '0':
            approved_qs = approved_qs.filter(project_id=project_id)
            pending_qs = pending_qs.filter(project_id=project_id)
            all_qs = all_qs.filter(project_id=project_id)
            user_qs = user_qs.filter(project_id=project_id)
            project_obj = Project.objects.filter(pk=project_id).first()

        context = {
            'is_manager': is_manager,
            'selected_project': project_obj,
            'all_projects': Project.objects.all(),
        }

        if is_manager:
            # Global total of approved cash
            global_total = approved_qs.aggregate(total=Sum('amount_requested'))['total'] or 0
            # Per‑project totals of approved cash
            per_project = (
                approved_qs.values('project__project_name')
                .annotate(total_given=Sum('amount_requested'))
            )
            context.update({
                'global_total': global_total,
                'per_project': per_project,
                'pending_requests': pending_qs,
                'all_requests': all_qs.order_by('-date_requested'),
            })
        else:
            # Staff view – list all projects and user's own requests
            projects = Project.objects.all()
            context.update({
                'projects': projects,
                'user_requests': user_qs.order_by('-date_requested'),
            })
        return render(request, self.template_name, context)

    def post(self, request):
        # Level 1/read-only user cannot request cash
        if not (request.user.is_superuser or request.user.groups.filter(name__in=['Level 2', 'Level 3', 'Level 4']).exists()):
            messages.error(request, "You do not have permission to submit cash requests.")
            return redirect('logistic:cash_requests_dashboard')

        # Staff can create a request here; managers should not use this endpoint
        if request.user.is_superuser or request.user.groups.filter(name__in=['Level 3', 'Level 4']).exists():
            messages.error(request, "Managers cannot submit cash requests on this page.")
            return redirect('logistic:cash_requests_dashboard')
        project_id = request.POST.get('project_id')
        milestone_title = request.POST.get('milestone_title', '').strip()
        amount = request.POST.get('amount_requested')
        justification = request.POST.get('justification', '')
        print(project_id, milestone_title, amount, justification)
        print(request.POST)
        if not project_id or not amount or not milestone_title:
            messages.error(request, "Project, milestone title, and amount are required.")
            return redirect('logistic:cash_requests_dashboard')
        MilestoneCashRequest.objects.create(
            project_id=project_id,
            milestone_title=milestone_title,
            amount_requested=amount,
            justification_notes=justification,
            requested_by=request.user,
            status='PENDING',
        )
        messages.success(request, "Cash request submitted.")
        return redirect('logistic:cash_requests_dashboard')