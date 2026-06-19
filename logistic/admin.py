from django.contrib import admin
from .models import MilestoneCashRequest, SiteStore, SiteUsageLog


admin.site.register(MilestoneCashRequest)
admin.site.register(SiteStore)
admin.site.register(SiteUsageLog)