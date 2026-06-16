from django.contrib import admin
from .models import Project, Account, Material, Request, Record, Store, Usage

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'balance', 'currency')
    list_filter = ('currency',)
    search_fields = ('name', 'project__name')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'unit', 'standard_price')
    list_filter = ('unit',)
    search_fields = ('name', 'project__name')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('material', 'project', 'quantity', 'status', 'date_requested')
    list_filter = ('status', 'date_requested')
    search_fields = ('material__name', 'project__name')

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('material', 'project', 'amount', 'quantity', 'total_cost', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('material__name', 'project__name')

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('material', 'project', 'current_stock', 'reorder_level')
    list_filter = ('project',)
    search_fields = ('material__name', 'project__name')

@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ('material', 'project', 'quantity', 'date')
    list_filter = ('date',)
    search_fields = ('material__name', 'project__name')
