from django.urls import path
from .views import (
    ProjectLogisticsDashboardView,
    AddSiteStoreInventoryView,
    MilestoneCashRequestCreateView,
    LogSiteUsageCreateView,
    ProcessCashRequestView,
    CashRequestDashboardView
)

app_name = 'logistic'

urlpatterns = [
    # Main site logistics dashboard (inventory + cash requests + usage)
    path('project/<int:project_id>/logistics/', ProjectLogisticsDashboardView.as_view(), name='project_logistics_hub'),

    # Add new material or restock existing inventory item
    path('project/<int:project_id>/logistics/add-inventory/', AddSiteStoreInventoryView.as_view(), name='add_inventory'),

    # Civil engineer submits a milestone-based cash request
    path('project/<int:project_id>/logistics/request-cash/', MilestoneCashRequestCreateView.as_view(), name='request_cash'),

    # Engineer logs on-site material consumption
    path('project/<int:project_id>/logistics/log-usage/', LogSiteUsageCreateView.as_view(), name='log_usage'),

    # Centralised cash request dashboard
    path('cash-requests/', CashRequestDashboardView.as_view(), name='cash_requests_dashboard'),

    # Management approves or rejects a pending cash request
    path('cash-request/<int:request_id>/process/', ProcessCashRequestView.as_view(), name='process_cash_request'),
]