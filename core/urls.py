from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    # Landing page / root
    path('', views.DashboardView.as_view(), name='home'),
    # # Auth routes
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('project/<int:pk>/select/', views.ProjectSwitcherView.as_view(), name='select_project'),
    path('records/', views.RecordListView.as_view(), name='record_list'),
    
    # Export routes
    path('records/export/excel/', views.ExportRecordsExcelView.as_view(), name='records_export_excel'),
    path('requests/export/excel/', views.ExportRequestsExcelView.as_view(), name='requests_export_excel'),
    path('accounts/export/excel/', views.ExportAccountsExcelView.as_view(), name='accounts_export_excel'),
    path('stores/export/excel/', views.ExportStoreExcelView.as_view(), name='stores_export_excel'),
    path('usage/export/excel/', views.ExportUsageExcelView.as_view(), name='usage_export_excel'),
]
