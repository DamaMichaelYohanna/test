from django.urls import path
from . import views

app_name='contractors'
urlpatterns = [
    path('', views.SubcontractorListView.as_view(), name='contractor_list'),
    path('add/', views.add_subcontractor, name='add_subcontractor'),
    path('edit/<int:pk>/', views.edit_subcontractor, name='edit_subcontractor'),
    path('delete/<int:pk>/', views.delete_subcontractor, name='delete_subcontractor'),
    path('compliance/', views.ComplianceMatrixView.as_view(), name='compliance_matrix'),
    path('compliance/manage/', views.ManageComplianceView.as_view(), name='manage_compliance'),
    path('compliance/requirements/', views.manage_compliance_requirements, name='manage_compliance_requirements'),
]   