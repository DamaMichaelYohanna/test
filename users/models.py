from django.contrib.auth.models import Group, User
from django.db import models


class JobTitle(models.Model):
    """
    Dynamic table for company designations.
    Allows adding new titles through the UI.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., Group Managing Director, Civil Engineer, Procurement Specialist",
    )
    permission_group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name='job_titles',
        help_text='Which foundational access level does this title map to?'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Job Title'
        verbose_name_plural = 'Job Titles'

    def __str__(self):
        return f"{self.name} ({self.permission_group.name})"


class Profile(models.Model):
    """
    Extends the base user account to link employees to their dynamic titles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.PROTECT,
        related_name='employees',
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    last_active_project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_2fa_enabled = models.BooleanField(
        default=False, 
        verbose_name="2FA Activated",
        help_text="Designates whether Two-Factor Authentication is activated for this account."
    )

    def __str__(self):
        title = self.job_title.name if self.job_title else 'No Title Assigned'
        return f"{self.user.get_full_name()} - {title}"
