from django.db import models
from projects.models import Project
from django.contrib.auth.models import User

class SiteStore(models.Model):
    """
    Replaces the central warehouse. Tracks physical stock levels 
    locally on a specific construction site.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="site_inventory")
    material_name = models.CharField(max_length=150, help_text="e.g., Cement, 16mm Rebar, Screeding Paint")
    quantity_on_site = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_of_measurement = models.CharField(max_length=50, help_text="e.g., Bags, Tons, Liters")
    last_restocked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'material_name')
        verbose_name = "Site Store Inventory"
        verbose_name_plural = "Site Store Inventories"

    def __str__(self):
        return f"{self.material_name} at [{self.project.project_code}] - Qty: {self.quantity_on_site}"


class MilestoneCashRequest(models.Model):
    """
    Replaces the material request. Civil Engineers request funds 
    tied directly to a project milestone framework.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Management Approval'),
        ('APPROVED', 'Approved & Funded'),
        ('REJECTED', 'Rejected / Clarification Needed'),
        ('CANCELLED', 'Cancelled'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="cash_requests")
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    milestone_title = models.CharField(max_length=255, help_text="e.g., Foundation Pouring, Blockwork Level 1")
    amount_requested = models.DecimalField(max_digits=15, decimal_places=2)
    justification_notes = models.TextField(help_text="Engineer's breakdown of what the money will execute.")
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    date_requested = models.DateTimeField(auto_now_add=True)
    date_actioned = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"₦{self.amount_requested} Request for {self.milestone_title} ({self.project.project_code})"


class SiteUsageLog(models.Model):
    """
    Tracks consumption on site. When materials are mixed/used, 
    it subtracts from the specific SiteStore.
    """
    site_store = models.ForeignKey(SiteStore, on_delete=models.CASCADE, related_name="usage_logs")
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    date_used = models.DateField()
    activity_details = models.CharField(max_length=255, help_text="e.g., Casted pillar alignment 1-5")

    def __str__(self):
        return f"{self.quantity_used} units used on {self.site_store.project.project_code}"