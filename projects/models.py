from django.db import models
from contractors.models import Subcontractor
from django.contrib.auth.models import User

class Project(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('CONSTRUCTION', 'Construction / Civil Works'),
        ('SUPPLY_TRAINING', 'Supply and Training Project'),
    ]

    PHASE_CHOICES = [
        ('PRE_AWARD', 'Bidding / Pre-Award Phase'),
        ('POST_AWARD', 'Execution / Post-Award Phase'),
        ('PAYMENT_PROCESSING', 'Application & Payment Processing'),
        ('COMPLETED', 'Project Fully Closed / Paid'),
    ]

    # --- Core Identifiers ---
    sn = models.AutoField(primary_key=True, verbose_name="S/N")
    mda = models.CharField(max_length=255, verbose_name="MDA", help_text="Ministry, Department, or Agency")
    project_code = models.CharField(max_length=100, unique=True, verbose_name="Project Code")
    project_name = models.CharField(max_length=512, verbose_name="Project Name")
    lot = models.CharField(max_length=50, blank=True, null=True, verbose_name="Lot")
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='CONSTRUCTION', verbose_name="Type")
    location = models.CharField(max_length=255, verbose_name="Location")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Category")
    
    # --- Documents & Attachments ---
    plain_boq = models.FileField(upload_to='projects/boq/plain/', blank=True, null=True, verbose_name="Plain BOQ")
    drawing_design = models.FileField(upload_to='projects/drawings/', blank=True, null=True, verbose_name="Drawing/Design")
    award_letter_and_boq = models.FileField(upload_to='projects/boq/awarded/', blank=True, null=True, verbose_name="Award Letter and BOQ")

    # --- Bidding / Pre-Award Phase Tracking ---
    final_companies = models.TextField(blank=True, null=True, verbose_name="Final Companies")
    back_up_companies = models.TextField(blank=True, null=True, verbose_name="Back up Companies")
    updated_recommended_companies = models.TextField(blank=True, null=True, verbose_name="Updated Recommended Companies")
    technical_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Technical")
    financial_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Financials")

    # --- Company Financial Pillars ---
    budget_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Budget Amount")
    actual_contract_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Actual Contract Amount")
    admin_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Admin Fee")
    
    # --- Internal Benchmarking ---
    in_house_benchmark = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="In-House Benchmark (Direct Labour)")
    cost_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Cost Percentage", help_text="e.g., 65.50 for 65.5%")

    # --- Inflow / Treasury Invoicing ---
    mobilization_received = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Mobilization Received")
    batch_no_mobilization = models.CharField(max_length=100, blank=True, null=True, verbose_name="Batch No. Mobilization")
    batch_no_final_payment = models.CharField(max_length=100, blank=True, null=True, verbose_name="Batch No. Final Payment")
    final_payment_received = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Final Payment Received")

    # --- Management & Status Flags ---
    staff_assigned = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Staff Assigned")
    current_phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='PRE_AWARD')
    level_of_completion_percentage = models.PositiveIntegerField(default=0, verbose_name="Level of Completion %")
    project_status = models.CharField(max_length=100, default="Initiated", verbose_name="Project Status")
    payment_status = models.CharField(max_length=100, default="Pending", verbose_name="Payment Status")
    comments = models.TextField(blank=True, null=True, verbose_name="Comments")
    remarks = models.TextField(blank=True, null=True, verbose_name="Remarks")

    # --- Intermediary Link for Shared/Split Subcontracting ---
    subcontractors = models.ManyToManyField(
        Subcontractor, 
        through='ProjectAllocation', 
        related_name='assigned_projects'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.project_code} - {self.mda} - {self.project_name}"



class ProjectAllocation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    subcontractor = models.ForeignKey(Subcontractor, on_delete=models.CASCADE, verbose_name="Sub-Contractor")
    
    # --- Subcontractor Technical Layouts ---
    sub_contractor_drawing_design = models.FileField(upload_to='subcontractors/drawings/', blank=True, null=True, verbose_name="Sub-Contractor Drawing/Design")
    supplier_contractor_price_boq = models.FileField(upload_to='subcontractors/boq/', blank=True, null=True, verbose_name="Supplier/Contractor Price 1/BOQ")
    
    # --- Allocation Financials ---
    sub_contractor_cost_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Sub-Contractor Cost Percentage")
    amount_agreed_with_supplier_contractor = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Amount Agreed with Supplier/Contractor")
    advance_received_by_supplier_contractor = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Advance Received by Supplier/Contractor")
    
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'subcontractor')
        verbose_name = "Project Subcontractor Allocation"
        verbose_name_plural = "Project Subcontractor Allocations"

    def __str__(self):
        return f"{self.project.project_code} assigned to {self.subcontractor.name}"

    @property
    def remaining_balance(self):
        """Calculates balance remaining for the subcontractor payment schedule."""
        return self.amount_agreed_with_supplier_contractor - self.advance_received_by_supplier_contractor


class ProjectLifecycleStage(models.Model):
    """
    Tracks the completion state and financial footprint of each phase 
    defined in your organizational framework template.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='lifecycle_stages')
    stage_name = models.CharField(max_length=255, help_text="e.g., 'Bi-weekly Purchase of Federal Tender Journal', 'Submission of Batch Numbers to AGF'")
    
    # Order sorting
    sequence_order = models.PositiveIntegerField(help_text="Determines the workflow pipeline order sequence")
    
    # Completion state metrics
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    notes_or_updates = models.TextField(blank=True, null=True, help_text="Use this to log internal processing stage and file movement details")
    
    # Framework Rule: 'All stages within the project lifecycle incur costs and should be appropriately captured'
    incurred_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00, 
        help_text="Capture processing costs, profile updates, journal purchase costs, or follow-up expenses here."
    )

    class Meta:
        ordering = ['sequence_order']
        unique_together = ('project', 'stage_name')

    def __str__(self):
        return f"{self.project.project_name} - Step {self.sequence_order}: {self.stage_name} [{'Done' if self.is_completed else 'Pending'}]"


class UnplannedExpense(models.Model):
    """
    Captures ad-hoc or unplanned project costs that do not fall within
    the defined lifecycle pipeline or milestone cash request schedule.
    These are added instantly without any approval workflow.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='unplanned_expenses',
    )
    description = models.CharField(
        max_length=255,
        help_text="Brief description of what the expense was for."
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Total amount of the unplanned expense."
    )
    date_incurred = models.DateField(
        help_text="Date the expense was incurred."
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_expenses',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_incurred']
        verbose_name = "Unplanned Expense"
        verbose_name_plural = "Unplanned Expenses"

    def __str__(self):
        return f"{self.project.project_code} — {self.description} (₦{self.amount:,.2f})"
