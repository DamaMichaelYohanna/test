from django.contrib import admin
from .models import UnplannedExpense


@admin.register(UnplannedExpense)
class UnplannedExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'description', 'amount', 'date_incurred', 'reported_by', 'created_at')
    list_filter = ('project', 'date_incurred')
    search_fields = ('description', 'project__project_name', 'project__project_code')
    date_hierarchy = 'date_incurred'
    ordering = ('-date_incurred',)
