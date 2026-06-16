from django.db import models

from django.db import models

class Subcontractor(models.Model):
    COMPANY_TYPE_CHOICES = [
        ('INTERNAL', 'Our Company (Internal Team)'),
        ('EXTERNAL', 'Outside Subcontractor'),
    ]
    name = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Name of the subcontracting company or internal department."
    )
    company_type = models.CharField(
        max_length=10,
        choices=COMPANY_TYPE_CHOICES,
        default='EXTERNAL',
        help_text="Is this an internal company or an outside sub-contractor?"
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Subcontractor"
        verbose_name_plural = "Subcontractors"

    def __str__(self):
        return f"{self.name} ({self.get_company_type_display()})"


class ComplianceRequirement(models.Model):
    """
    The Master List of required documents. 
    Examples: 'Tax Audit', 'COREN Registration', 'Workmen Compensation Insurance'
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Brief description of what this document entails.")
    is_mandatory = models.BooleanField(default=True, help_text="Is this document strictly required for all contractors?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SubcontractorCompliance(models.Model):
    """
    The main tracking matrix. Links a Subcontractor to a specific requirement, 
    for a specific calendar year.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Missing / Outstanding'),
        ('SUBMITTED', 'Submitted / Under Review'),
        ('APPROVED', 'Approved & Valid'),
        ('EXPIRED', 'Expired / Needs Renewal'),
    ]

    subcontractor = models.ForeignKey(
        Subcontractor, 
        on_delete=models.CASCADE, 
        related_name='compliance_records'
    )
    requirement = models.ForeignKey(
        ComplianceRequirement, 
        on_delete=models.PROTECT, 
        related_name='subcontractor_records'
    )
    year = models.PositiveIntegerField(
        help_text="The calendar year this compliance record belongs to (e.g., 2026)"
    )
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    
    # Optional document upload field if your superior wants to see the actual document
    uploaded_file = models.FileField(upload_to='compliance_docs/%Y/', blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True, help_text="If the document expires mid-year.")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Crucial safety constraint: Prevents duplicate tracking entries for the same doc, company, and year.
        unique_together = ('subcontractor', 'requirement', 'year')
        ordering = ['-year', 'requirement__name']

    def __str__(self):
        return f"{self.subcontractor.name} - {self.requirement.name} ({self.year}) - {self.get_status_display()}"