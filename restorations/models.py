from django.db import models
from django.utils import timezone

class Restoration(models.Model):
    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey('equipments.Equipment', on_delete=models.CASCADE) 
    restoration_date = models.DateTimeField(null=False)
    performed_by = models.CharField(max_length=100, null=False)
    description = models.TextField(blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_delivery_date = models.DateTimeField(null=False)
    delivery_date = models.DateTimeField(null=False)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    invoice_date = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=100, null=False)
    created_on = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Restoration {self.id} for Equipment {self.equipment_id}'