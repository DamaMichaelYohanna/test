from django.contrib import admin

from .models import JobTitle, Profile


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission_group')
    search_fields = ('name', 'permission_group__name')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'phone_number', 'last_active_project')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_select_related = ('user', 'job_title', 'last_active_project')
