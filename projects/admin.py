from django.contrib import admin
from .models import Project, ProjectCategory, FeeType, ProjectFee, UnplannedExpense

class ProjectFeeInline(admin.TabularInline):
    model = ProjectFee
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'mda', 'project_name', 'project_type', 'current_phase', 'budget_amount', 'actual_contract_amount')
    list_filter = ('project_type', 'current_phase', 'category')
    search_fields = ('project_code', 'project_name', 'mda')
    inlines = [ProjectFeeInline]

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(ProjectFee)
class ProjectFeeAdmin(admin.ModelAdmin):
    list_display = ('project', 'fee_type', 'amount')
    list_filter = ('fee_type',)
    search_fields = ('project__project_code', 'project__project_name')


@admin.register(UnplannedExpense)
class UnplannedExpenseAdmin(admin.ModelAdmin):
    list_display = ('project', 'description', 'amount', 'date_incurred', 'reported_by', 'created_at')
    list_filter = ('project', 'date_incurred')
    search_fields = ('description', 'project__project_name', 'project__project_code')
    date_hierarchy = 'date_incurred'
    ordering = ('-date_incurred',)
