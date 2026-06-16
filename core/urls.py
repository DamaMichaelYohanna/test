from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    # Landing page / root
    path('', views.DashboardView.as_view(), name='home'),
    # Auth routes
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('project/<int:pk>/select/', views.ProjectSwitcherView.as_view(), name='select_project'),
    path('records/', views.RecordListView.as_view(), name='record_list'),
    path('records/create/', views.RecordCreateView.as_view(), name='record_create'),
    path('records/<int:pk>/update/', views.RecordUpdateView.as_view(), name='record_update'),
    path('records/<int:pk>/delete/', views.RecordDeleteView.as_view(), name='record_delete'),
    path('requests/', views.RequestListView.as_view(), name='request_list'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/update/', views.RequestUpdateView.as_view(), name='request_update'),
    path('requests/<int:pk>/delete/', views.RequestDeleteView.as_view(), name='request_delete'),
    # Account routes
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    # Inventory (Material) routes
    path('inventory/', views.MaterialListView.as_view(), name='material_list'),
    path('inventory/create/', views.MaterialCreateView.as_view(), name='material_create'),
    path('inventory/<int:pk>/update/', views.MaterialUpdateView.as_view(), name='material_update'),
    path('inventory/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='material_delete'),
    # Store routes
    path('stores/', views.StoreListView.as_view(), name='store_list'),
    path('stores/create/', views.StoreCreateView.as_view(), name='store_create'),
    path('stores/<int:pk>/update/', views.StoreUpdateView.as_view(), name='store_update'),
    path('stores/<int:pk>/delete/', views.StoreDeleteView.as_view(), name='store_delete'),
    # Usage routes
    path('usage/', views.UsageListView.as_view(), name='usage_list'),
    path('usage/create/', views.UsageCreateView.as_view(), name='usage_create'),
    path('usage/<int:pk>/update/', views.UsageUpdateView.as_view(), name='usage_update'),
    path('usage/<int:pk>/delete/', views.UsageDeleteView.as_view(), name='usage_delete'),
    # Budget routes
    path('budget/', views.BudgetView.as_view(), name='budget_summary'),

    # Export routes
    path('records/export/excel/', views.ExportRecordsExcelView.as_view(), name='records_export_excel'),
    path('requests/export/excel/', views.ExportRequestsExcelView.as_view(), name='requests_export_excel'),
    path('accounts/export/excel/', views.ExportAccountsExcelView.as_view(), name='accounts_export_excel'),
    path('stores/export/excel/', views.ExportStoreExcelView.as_view(), name='stores_export_excel'),
    path('usage/export/excel/', views.ExportUsageExcelView.as_view(), name='usage_export_excel'),
]
