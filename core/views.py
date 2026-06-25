from decimal import Decimal
from django.contrib import messages     
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from projects.models import Project
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import openpyxl

from projects.models import ProjectLifecycleStage, Project, UnplannedExpense
from logistic.models import MilestoneCashRequest


def logout_view(request):
    """Log out the user and redirect to login page.
    Accepts GET requests to avoid 405 errors.
    """
    from django.contrib.auth import logout
    logout(request)
    return redirect('core:login')



class ProjectRequiredMixin(LoginRequiredMixin):
    """Mixin to filter querysets by the project selected in the session.
    All views that inherit this mixin will have a ``self.project`` attribute
    representing the currently active project (or ``None`` if not selected).
    """

    def dispatch(self, request, *args, **kwargs):
        project_id = request.GET.get("project")
        self.project = None
        if project_id and project_id != '0':
            self.project = get_object_or_404(Project, pk=project_id)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self, "project", None):
            # Assume the model has a ``project`` FK; filter accordingly.
            if "project" in [f.name for f in qs.model._meta.get_fields()]:
                qs = qs.filter(project=self.project)
        return qs


class ProjectSwitcherView(LoginRequiredMixin, View):
    """Simple view that stores the chosen project ID in the session.
    URL pattern: ``project/<int:pk>/select/``.
    After switching, redirects back to the page that requested the switch
    (using ``HTTP_REFERER``) or to the dashboard as a fallback.
    """

    def get(self, request, pk):
        from urllib.parse import urlparse
        from django.urls import resolve, reverse, Resolver404

        if pk == 0:
            if "project_id" in request.session:
                del request.session["project_id"]
            if "project_name" in request.session:
                del request.session["project_name"]
        else:
            # Validate the project exists.
            project = get_object_or_404(Project, pk=pk)
            request.session["project_id"] = project.sn
            request.session["project_name"] = project.project_code

        # Redirect back.
        next_url = request.META.get("HTTP_REFERER") or reverse("core:dashboard")
        
        if request.META.get("HTTP_REFERER"):
            parsed = urlparse(next_url)
            try:
                match = resolve(parsed.path)
                if 'project_id' in match.kwargs:
                    if pk == 0:
                        # Cannot stay on a project-specific page if "ALL" is selected
                        next_url = reverse("core:dashboard")
                    else:
                        match.kwargs['project_id'] = pk
                        next_url = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
                elif 'pk' in match.kwargs and match.view_name.startswith('projects:'):
                    # For project detail pages, 'pk' might be the project id
                    if pk == 0:
                        next_url = reverse("core:dashboard")
                    else:
                        match.kwargs['pk'] = pk
                        next_url = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
            except Resolver404:
                pass

        return redirect(next_url)


class ExpensesDashboardView(ProjectRequiredMixin, TemplateView):
    template_name = "expenses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.project:
            stages = ProjectLifecycleStage.objects.filter(project=self.project)
            cash_requests = MilestoneCashRequest.objects.filter(project=self.project)
            unplanned = UnplannedExpense.objects.filter(project=self.project)
        else:
            stages = ProjectLifecycleStage.objects.all()
            cash_requests = MilestoneCashRequest.objects.all()
            unplanned = UnplannedExpense.objects.all()

        stage_costs = stages.aggregate(total=Sum('incurred_cost'))['total'] or Decimal('0.00')
        cash_request_costs = cash_requests.filter(status='APPROVED').aggregate(total=Sum('amount_requested'))['total'] or Decimal('0.00')
        unplanned_costs = unplanned.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        per_project_expenses = []
        if not self.project:
            for p in Project.objects.all():
                p_stage = ProjectLifecycleStage.objects.filter(project=p).aggregate(total=Sum('incurred_cost'))['total'] or Decimal('0.00')
                p_cash = MilestoneCashRequest.objects.filter(project=p, status='APPROVED').aggregate(total=Sum('amount_requested'))['total'] or Decimal('0.00')
                p_unplanned = UnplannedExpense.objects.filter(project=p).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                if p_stage > 0 or p_cash > 0 or p_unplanned > 0:
                    per_project_expenses.append({
                        'project': p,
                        'stage_costs': p_stage,
                        'cash_request_costs': p_cash,
                        'unplanned_costs': p_unplanned,
                        'total': Decimal(p_stage) + Decimal(p_cash) + Decimal(p_unplanned)
                    })

        context.update({
            'total_stage_costs': stage_costs,
            'total_cash_request_costs': cash_request_costs,
            'total_unplanned_costs': unplanned_costs,
            'total_expenses': Decimal(stage_costs) + Decimal(cash_request_costs) + Decimal(unplanned_costs),
            'per_project_expenses': per_project_expenses,
            'recent_stages': stages.filter(incurred_cost__gt=0).order_by('-completed_date')[:50],
            'recent_cash_requests': cash_requests.filter(status='APPROVED').order_by('-date_requested')[:50],
            'recent_unplanned': unplanned.select_related('reported_by', 'project').order_by('-date_incurred')[:50],
        })
        return context


class UnplannedExpenseCreateView(LoginRequiredMixin, View):
    """Allows any logged-in user to instantly log an unplanned project expense."""
    template_name = 'core/unplanned_expense_form.html'

    def get(self, request):
        projects = Project.objects.all()
        preselect = request.GET.get('project')
        return render(request, self.template_name, {
            'projects': projects,
            'preselect': preselect,
        })

    def post(self, request):
        project_id = request.POST.get('project_id')
        description = request.POST.get('description', '').strip()
        amount = request.POST.get('amount', '').strip()
        date_incurred = request.POST.get('date_incurred', '').strip()

        if not project_id or not description or not amount or not date_incurred:
            messages.error(request, "Project, description, amount, and date are all required.")
            return redirect('core:add_unplanned_expense')

        try:
            project = get_object_or_404(Project, pk=project_id)
            UnplannedExpense.objects.create(
                project=project,
                description=description,
                amount=Decimal(amount),
                date_incurred=date_incurred,
                reported_by=request.user,
            )
            messages.success(request, f"Unplanned expense of ₦{Decimal(amount):,.2f} logged for {project.project_code}.")
        except Exception as e:
            messages.error(request, f"Could not save expense: {e}")
        return redirect('core:expenses_dashboard')


class DashboardView(ProjectRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from projects.models import Project, ProjectAllocation, ProjectLifecycleStage
        from contractors.models import Subcontractor, Company, CompanyCompliance
        from logistic.models import SiteStore, MilestoneCashRequest
        
        # 1. Scope determination
        if self.project:
            projects_qs = Project.objects.filter(sn=self.project.sn)
            allocations_qs = ProjectAllocation.objects.filter(project=self.project)
            cash_requests_qs = MilestoneCashRequest.objects.filter(project=self.project)
            stores_qs = SiteStore.objects.filter(project=self.project)
        else:
            projects_qs = Project.objects.all()
            allocations_qs = ProjectAllocation.objects.all()
            cash_requests_qs = MilestoneCashRequest.objects.all()
            stores_qs = SiteStore.objects.all()
            
        # 2. Role-Based Access Guards
        user = self.request.user
        user_groups = list(user.groups.values_list('name', flat=True)) if user.is_authenticated else []
        is_executive_or_management = (
            user.is_superuser or 
            any(g in ['Executive', 'Management', 'Level 3', 'Level 4'] for g in user_groups)
        )
        if 'Technical/Field' in user_groups:
            is_executive_or_management = False
            
        # 3. Layer A: Executive Financial KPI Cards
        # Total Contract Value Portfolio
        total_contract_value = projects_qs.aggregate(val=Sum('actual_contract_amount'))['val'] or 0.0
        
        # Expected Gross Profit Margin Panel
        total_in_house_benchmark = projects_qs.aggregate(val=Sum('in_house_benchmark'))['val'] or 0.0
        
        if total_contract_value > 0:
            cost_percentage = (Decimal(total_in_house_benchmark) / Decimal(total_contract_value)) * 100

        else:
            cost_percentage = 0.0
        gross_profit_margin = 100.0 - float(cost_percentage)
        
        # Total Disbursed Capital
        total_disbursed_capital = projects_qs.aggregate(
            val=Sum(F('mobilization_received') + F('final_payment_received'))
        )['val'] or 0.0
        
        # Subcontractor Exposure Liability
        subcontractor_exposure = allocations_qs.aggregate(
            val=Sum(F('amount_agreed_with_supplier_contractor') - F('advance_received_by_supplier_contractor'))
        )['val'] or 0.0
        
        # 4. Layer B: Bidding Strategy & File Tracking Pipeline
        active_bidding_pipeline = projects_qs.filter(current_phase='PRE_AWARD')
        
        project_roadmaps = []
        for p in projects_qs:
            stages_list = p.lifecycle_stages.all().order_by('sequence_order')
            audit_stage = next((s for s in stages_list if "Head of Audit" in s.stage_name), None)
            procurement_stage = next((s for s in stages_list if "Procurement Office" in s.stage_name), None)
            store_stage = next((s for s in stages_list if "Store Department" in s.stage_name), None)
            finance_stage = next((s for s in stages_list if "Director of Finance" in s.stage_name), None)
            agf_stage = next((s for s in stages_list if "Confirmation of Payment" in s.stage_name or "Certified Status" in s.stage_name or "AGF" in s.stage_name), None)
            
            p_status = (p.payment_status or "").strip().lower()
            p_batch = (p.batch_no_final_payment or "").strip()
            is_alert = (p_status == "uploaded for payment" and not p_batch)
            
            project_roadmaps.append({
                'project_code': p.project_code,
                'project_name': p.project_name,
                'payment_status': p.payment_status,
                'batch_no_final_payment': p.batch_no_final_payment,
                'is_alert': is_alert,
                'stages': [
                    {'name': 'Head of Audit', 'is_completed': audit_stage.is_completed if audit_stage else False, 'notes': audit_stage.notes_or_updates if audit_stage else ''},
                    {'name': 'Procurement Office', 'is_completed': procurement_stage.is_completed if procurement_stage else False, 'notes': procurement_stage.notes_or_updates if procurement_stage else ''},
                    {'name': 'Store Department', 'is_completed': store_stage.is_completed if store_stage else False, 'notes': store_stage.notes_or_updates if store_stage else ''},
                    {'name': 'Director of Finance', 'is_completed': finance_stage.is_completed if finance_stage else False, 'notes': finance_stage.notes_or_updates if finance_stage else ''},
                    {'name': 'AGF Payment', 'is_completed': agf_stage.is_completed if agf_stage else False, 'notes': agf_stage.notes_or_updates if agf_stage else ''},
                ]
            })
            
        # 5. Layer C: Field Operations & Subcontractor Health
        # Progress vs Budget Burn-Rate Variance
        project_variances = []
        for p in projects_qs:
            drawn_down = MilestoneCashRequest.objects.filter(project=p, status='APPROVED').aggregate(total=Sum('amount_requested'))['total'] or 0.0
            drawdown_rate = (float(drawn_down) / float(p.budget_amount) * 100) if p.budget_amount > 0 else 0.0
            completion_rate = p.level_of_completion_percentage
            variance = completion_rate - drawdown_rate
            exceeds = drawdown_rate > completion_rate
            project_variances.append({
                'project_code': p.project_code,
                'project_name': p.project_name,
                'budget_amount': p.budget_amount,
                'drawn_down': drawn_down,
                'drawdown_rate': round(drawdown_rate, 2),
                'completion_rate': completion_rate,
                'variance': round(variance, 2),
                'exceeds': exceeds,
            })
            
        # Allocation Spread
        external_pct = allocations_qs.aggregate(total=Sum('sub_contractor_cost_percentage'))['total'] or 0.0
        external_pct = float(external_pct)
        in_house_pct = max(0.0, 100.0 - external_pct)
        
        # 6. Layer D: Field Operations Action Items
        # Pending Milestone Cash Requests
        pending_cash_requests = cash_requests_qs.filter(status='PENDING').select_related('project', 'requested_by')
        
        # Material Deficiency Alerts
        material_alerts = stores_qs.filter(quantity_on_site=0).select_related('project')
        
        # Vendor Compliance Safeguards
        current_year = timezone.now().year
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        compliance_alerts = CompanyCompliance.objects.filter(
            year=current_year
        ).filter(
            Q(status__in=['PENDING', 'EXPIRED']) |
            Q(status='APPROVED', expiry_date__lte=thirty_days_later)
        ).select_related('company', 'requirement').order_by('company__name', 'requirement__name')
        
        context.update({
            'is_executive_or_management': is_executive_or_management,
            'total_contract_value': total_contract_value,
            'total_in_house_benchmark': total_in_house_benchmark,
            'cost_percentage': round(cost_percentage, 2),
            'gross_profit_margin': round(gross_profit_margin, 2),
            'total_disbursed_capital': total_disbursed_capital,
            'subcontractor_exposure': subcontractor_exposure,
            'active_bidding_pipeline': active_bidding_pipeline,
            'project_roadmaps': project_roadmaps,
            'project_variances': project_variances,
            'external_pct': external_pct,
            'in_house_pct': in_house_pct,
            'pending_cash_requests': pending_cash_requests,
            'material_alerts': material_alerts,
            'compliance_alerts': compliance_alerts,
            'project': self.project,
            'total_projects': Project.objects.count(),
            'internal_contractors': Subcontractor.objects.filter(company_type='INTERNAL').count(),
            'external_contractors': Subcontractor.objects.filter(company_type='EXTERNAL').count(),
        })
        return context

