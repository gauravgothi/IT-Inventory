from django.db import models
from django.utils import timezone
from orders.models import Order

class Equipment(models.Model):
    # Fields corresponding to the equipment table
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100, null=False)
    sub_category = models.CharField(max_length=100, null=False)
    name = models.CharField(max_length=100, null=False)
    make = models.CharField(max_length=100, null=False)
    model = models.CharField(max_length=100, null=False)
    serial_number = models.CharField(max_length=50, unique=True, null=False)

    order = models.ForeignKey('orders.Order',on_delete=models.SET_NULL,null=True,blank=True)

    receipt_date = models.DateTimeField(null=True, blank=True)
    warranty_expiration = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='available')
    location = models.CharField(max_length=100, blank=True, null=True)
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    
    created_by = models.CharField(max_length=100, null=False)
    created_on = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.name} - {self.serial_number}'


