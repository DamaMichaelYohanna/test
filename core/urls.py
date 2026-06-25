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
    path('expenses/', views.ExpensesDashboardView.as_view(), name='expenses_dashboard'),
    path('expenses/unplanned/add/', views.UnplannedExpenseCreateView.as_view(), name='add_unplanned_expense'),
    path('project/<int:pk>/select/', views.ProjectSwitcherView.as_view(), name='select_project'),
    ]
