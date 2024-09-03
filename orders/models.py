from django.db import models
from django.utils import timezone

class Order(models.Model):
    # Fields corresponding to the equipment table
    id = models.AutoField(primary_key=True)
    po_number = models.CharField(max_length=20, null=False,unique=True)
    po_type=models.CharField(max_length=100,null=True)
    project_id = models.CharField(max_length=20, blank=True, null=True)
    project_name = models.CharField(max_length=150, blank=True, null=True)
    supplier_id = models.CharField(max_length=20, blank=True, null=True)
    supplier_name = models.CharField(max_length=150, blank=True, null=True)
    purchase_date = models.DateTimeField(null=True, blank=True)
    
    created_by = models.CharField(max_length=100, null=False)
    created_on = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.po_number} - {self.project_name}'
