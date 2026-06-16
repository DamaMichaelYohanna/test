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
from .models import Project, Record, Request, Store, Account, Material, Usage
from django.db.models import Sum, F
from django.http import HttpResponse
import openpyxl


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
        project_id = request.session.get("project_id")
        self.project = None
        if project_id:
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
        # Validate the project exists.
        project = get_object_or_404(Project, pk=pk)
        request.session["project_id"] = project.sn
        # Optional: store a friendly name for display.
        request.session["project_name"] = project.project_name
        # Redirect back.
        next_url = request.META.get("HTTP_REFERER") or reverse_lazy("core:dashboard")
        return redirect(next_url)


class DashboardView(ProjectRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If a project is selected, filter data; otherwise show aggregate for all.
        from projects.models import Project, ProjectLifecycleStage
        from contractors.models import Subcontractor

        if self.project:
            stages = ProjectLifecycleStage.objects.filter(project=self.project)
            records = Record.objects.filter(project=self.project)
            requests_qs = Request.objects.filter(project=self.project)
            stores = Store.objects.filter(project=self.project)
        else:
            stages = ProjectLifecycleStage.objects.all()
            records = Record.objects.all()
            requests_qs = Request.objects.all()
            stores = Store.objects.all()

        total_spent = stages.aggregate(total=Sum("incurred_cost"))["total"] or 0
        active_requests = requests_qs.filter(status="pending").count()
        low_stock = stores.filter(current_stock__lt=F("reorder_level"))
        wallets = Account.objects.filter(project=self.project) if self.project else Account.objects.all()
        wallet_balances = {w.name: w.balance for w in wallets}

        total_projects = Project.objects.count()
        internal_contractors = Subcontractor.objects.filter(company_type='INTERNAL').count()
        external_contractors = Subcontractor.objects.filter(company_type='EXTERNAL').count()

        context.update(
            {
                "total_spent": total_spent,
                "active_requests": active_requests,
                "low_stock": low_stock,
                "wallet_balances": wallet_balances,
                "project": self.project,
                "total_projects": total_projects,
                "internal_contractors": internal_contractors,
                "external_contractors": external_contractors,
            }
        )
        return context


# Generic CRUD views – they all inherit ProjectRequiredMixin to ensure proper scoping.
class RecordListView(ProjectRequiredMixin, ListView):
    model = Record
    template_name = "record_list.html"
    context_object_name = "records"

    def get_queryset(self):
        return super().get_queryset().select_related("material", "project")

class RecordCreateView(ProjectRequiredMixin, CreateView):
    model = Record
    fields = ["project", "material", "amount", "quantity", "bank_name", "account_number", "wallet"]
    template_name = "record_form.html"
    success_url = reverse_lazy("core:record_list")

    def form_valid(self, form):
        # Ensure the record belongs to the selected project if one is set.
        if self.project and not form.instance.project_id:
            form.instance.project = self.project
        return super().form_valid(form)

class RecordUpdateView(ProjectRequiredMixin, UpdateView):
    model = Record
    fields = ["material", "amount", "quantity", "bank_name", "account_number", "wallet"]
    template_name = "record_form.html"
    success_url = reverse_lazy("core:record_list")

class RecordDeleteView(ProjectRequiredMixin, DeleteView):
    model = Record
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:record_list")

# Requests CRUD – similar pattern.
class RequestListView(ProjectRequiredMixin, ListView):
    model = Request
    template_name = "request_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        return super().get_queryset().select_related("material", "project")

class RequestCreateView(ProjectRequiredMixin, CreateView):
    model = Request
    fields = ["project", "material", "quantity", "requested_by", "status"]
    template_name = "request_form.html"
    success_url = reverse_lazy("core:request_list")

    def form_valid(self, form):
        if self.project and not form.instance.project_id:
            form.instance.project = self.project
        return super().form_valid(form)

class RequestUpdateView(ProjectRequiredMixin, UpdateView):
    model = Request
    fields = ["material", "quantity", "status"]
    template_name = "request_form.html"
    success_url = reverse_lazy("core:request_list")

class RequestDeleteView(ProjectRequiredMixin, DeleteView):
    model = Request
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:request_list")

# Additional CRUD for Store, Usage, Account, Material can be added similarly.

# --- Account Views ---
class AccountListView(ProjectRequiredMixin, ListView):
    model = Account
    template_name = "account_list.html"
    context_object_name = "accounts"

class AccountCreateView(ProjectRequiredMixin, CreateView):
    model = Account
    fields = ["project", "name", "balance", "currency"]
    template_name = "account_form.html"
    success_url = reverse_lazy("core:account_list")

    def form_valid(self, form):
        if self.project and not form.instance.project_id:
            form.instance.project = self.project
        return super().form_valid(form)

class AccountUpdateView(ProjectRequiredMixin, UpdateView):
    model = Account
    fields = ["name", "balance", "currency"]
    template_name = "account_form.html"
    success_url = reverse_lazy("core:account_list")

class AccountDeleteView(ProjectRequiredMixin, DeleteView):
    model = Account
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:account_list")


# --- Inventory (Material) Views ---
class MaterialListView(ProjectRequiredMixin, ListView):
    model = Material
    template_name = "material_list.html"
    context_object_name = "materials"

class MaterialCreateView(ProjectRequiredMixin, CreateView):
    model = Material
    fields = ["project", "name", "description", "unit", "standard_price"]
    template_name = "material_form.html"
    success_url = reverse_lazy("core:material_list")

    def form_valid(self, form):
        if self.project and not form.instance.project_id:
            form.instance.project = self.project
        return super().form_valid(form)

class MaterialUpdateView(ProjectRequiredMixin, UpdateView):
    model = Material
    fields = ["name", "description", "unit", "standard_price"]
    template_name = "material_form.html"
    success_url = reverse_lazy("core:material_list")

class MaterialDeleteView(ProjectRequiredMixin, DeleteView):
    model = Material
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:material_list")


# --- Store Views ---
class StoreListView(ProjectRequiredMixin, ListView):
    model = Store
    template_name = "store_list.html"
    context_object_name = "stores"

    def get_queryset(self):
        return super().get_queryset().select_related("material", "project")

class StoreCreateView(ProjectRequiredMixin, CreateView):
    model = Store
    fields = ["project", "material", "current_stock", "reorder_level", "warehouse_location"]
    template_name = "store_form.html"
    success_url = reverse_lazy("core:store_list")

    def form_valid(self, form):
        if self.project and not form.instance.project_id:
            form.instance.project = self.project
        return super().form_valid(form)

class StoreUpdateView(ProjectRequiredMixin, UpdateView):
    model = Store
    fields = ["material", "current_stock", "reorder_level", "warehouse_location"]
    template_name = "store_form.html"
    success_url = reverse_lazy("core:store_list")

class StoreDeleteView(ProjectRequiredMixin, DeleteView):
    model = Store
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:store_list")


# --- Usage Views ---
class UsageListView(ProjectRequiredMixin, ListView):
    model = Usage
    template_name = "usage_list.html"
    context_object_name = "usages"

    def get_queryset(self):
        return super().get_queryset().select_related("material", "project")

class UsageCreateView(ProjectRequiredMixin, CreateView):
    model = Usage
    fields = ["project", "material", "quantity", "purpose"]
    template_name = "usage_form.html"
    success_url = reverse_lazy("core:usage_list")

    def form_valid(self, form):
        if self.project and not form.instance.project_id:
            form.instance.project = self.project
        return super().form_valid(form)

class UsageUpdateView(ProjectRequiredMixin, UpdateView):
    model = Usage
    fields = ["material", "quantity", "purpose"]
    template_name = "usage_form.html"
    success_url = reverse_lazy("core:usage_list")

class UsageDeleteView(ProjectRequiredMixin, DeleteView):
    model = Usage
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:usage_list")


# --- Budget View ---
class BudgetView(ProjectRequiredMixin, TemplateView):
    template_name = "budget_summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate budget details (total records cost vs available account balances)
        if self.project:
            records = Record.objects.filter(project=self.project)
            accounts = Account.objects.filter(project=self.project)
        else:
            records = Record.objects.all()
            accounts = Account.objects.all()

        total_expenditure = records.aggregate(total=Sum("total_cost"))["total"] or 0
        total_funds = accounts.aggregate(total=Sum("balance"))["total"] or 0
        net_budget = total_funds - total_expenditure

        context.update({
            "total_expenditure": total_expenditure,
            "total_funds": total_funds,
            "net_budget": net_budget,
            "project": self.project,
        })
        return context


# --- Project Management Views ---
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "project_list.html"
    context_object_name = "projects"

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ["name", "location", "start_date", "status"]
    template_name = "project_form.html"
    success_url = reverse_lazy("core:project_list")

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    fields = ["name", "location", "start_date", "status"]
    template_name = "project_form.html"
    success_url = reverse_lazy("core:project_list")

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("core:project_list")


# --- Excel Export Views ---
class ExportRecordsExcelView(ProjectRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Records"
        headers = ["S/N", "Created On", "Material", "Amount (NGN)", "Quantity", "Total Cost (NGN)", "Bank Name", "Account Number"]
        ws.append(headers)
        qs = Record.objects.filter(project=self.project).select_related("material") if self.project else Record.objects.all().select_related("material")
        for idx, r in enumerate(qs, 1):
            ws.append([idx, r.created_on.strftime("%Y-%m-%d") if r.created_on else "", r.material.name, float(r.amount), r.quantity, float(r.total_cost), r.bank_name, r.account_number])
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        pname = self.project.project_name if self.project else "All_Projects"
        response["Content-Disposition"] = f'attachment; filename="Records_{pname}.xlsx"'
        wb.save(response)
        return response


class ExportRequestsExcelView(ProjectRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Requests"
        ws.append(["S/N", "Date Requested", "Material", "Quantity", "Requested By", "Status"])
        qs = Request.objects.filter(project=self.project).select_related("material", "requested_by") if self.project else Request.objects.all().select_related("material", "requested_by")
        for idx, r in enumerate(qs, 1):
            ws.append([idx, r.date_requested.strftime("%Y-%m-%d") if r.date_requested else "", r.material.name, r.quantity, r.requested_by.username if r.requested_by else "-", r.status])
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        pname = self.project.project_name if self.project else "All_Projects"
        response["Content-Disposition"] = f'attachment; filename="Requests_{pname}.xlsx"'
        wb.save(response)
        return response


class ExportAccountsExcelView(ProjectRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Accounts"
        ws.append(["S/N", "Account Name", "Currency", "Balance", "Last Updated"])
        qs = Account.objects.filter(project=self.project) if self.project else Account.objects.all()
        for idx, a in enumerate(qs, 1):
            ws.append([idx, a.name, a.currency, float(a.balance), a.last_updated.strftime("%Y-%m-%d %H:%M") if a.last_updated else ""])
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        pname = self.project.project_name if self.project else "All_Projects"
        response["Content-Disposition"] = f'attachment; filename="Accounts_{pname}.xlsx"'
        wb.save(response)
        return response


class ExportStoreExcelView(ProjectRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Store"
        ws.append(["S/N", "Material", "Unit", "Current Stock", "Reorder Level", "Status", "Warehouse Location"])
        qs = Store.objects.filter(project=self.project).select_related("material") if self.project else Store.objects.all().select_related("material")
        for idx, s in enumerate(qs, 1):
            status = "Low Stock" if s.current_stock <= s.reorder_level else "Good"
            ws.append([idx, s.material.name, s.material.unit, s.current_stock, s.reorder_level, status, s.warehouse_location or "-"])
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        pname = self.project.project_name if self.project else "All_Projects"
        response["Content-Disposition"] = f'attachment; filename="Store_{pname}.xlsx"'
        wb.save(response)
        return response


class ExportUsageExcelView(ProjectRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Usage"
        ws.append(["S/N", "Date", "Material", "Quantity", "Unit", "Purpose"])
        qs = Usage.objects.filter(project=self.project).select_related("material") if self.project else Usage.objects.all().select_related("material")
        for idx, u in enumerate(qs, 1):
            ws.append([idx, u.date.strftime("%Y-%m-%d") if u.date else "", u.material.name, u.quantity, u.material.unit, u.purpose or "-"])
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        pname = self.project.project_name if self.project else "All_Projects"
        response["Content-Disposition"] = f'attachment; filename="Usage_{pname}.xlsx"'
        wb.save(response)
        return response



