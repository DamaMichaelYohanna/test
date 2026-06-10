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
    contact_person = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Primary contact person name."
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True
    )
    email = models.EmailField(
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