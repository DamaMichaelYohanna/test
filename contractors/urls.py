from django.urls import path
from . import views

app_name='contractors'
urlpatterns = [
    path('contractors/', views.SubcontractorListView.as_view(), name='contractor_list'),
    path('contractors/add/', views.add_subcontractor, name='add_subcontractor'),
    path('contractors/edit/<int:subcontractor_id>/', views.edit_subcontractor, name='edit_subcontractor'),
    path('contractors/delete/<int:subcontractor_id>/', views.delete_subcontractor, name='delete_subcontractor'),
]   