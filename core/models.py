from django.db import models
from django.contrib.auth.models import User

from projects.models import Project

class Account(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.currency})"

class Material(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50)
    standard_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name

class Request(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requests')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_requested = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.material.name} x {self.quantity} for {self.project.name}"

class Record(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='records')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # unit price
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    wallet = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_on = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.amount * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.name} - {self.total_cost}"

class Store(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stores')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    current_stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField()
    warehouse_location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.material.name} stock for {self.project.name}"

class Usage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='usages')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    purpose = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.material.name} used in {self.project.name}"
