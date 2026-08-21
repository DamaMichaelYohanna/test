from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/toggle-2fa/', views.toggle_2fa_view, name='toggle_2fa'),
    path('', views.UserListView.as_view(), name='user_list'),
    path('create/', views.UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('job-titles/', views.JobTitleListView.as_view(), name='jobtitle_list'),
    path('job-titles/create/', views.JobTitleCreateView.as_view(), name='jobtitle_create'),
    path('job-titles/<int:pk>/update/', views.JobTitleUpdateView.as_view(), name='jobtitle_update'),
    path('job-titles/<int:pk>/delete/', views.JobTitleDeleteView.as_view(), name='jobtitle_delete'),
]
