from django.db import models
from django.utils import timezone
from orders.models import Order
from miscellaneous.models import Status,Condition

class Equipment(models.Model):
    
    # Fields corresponding to the equipment table
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100, null=False)
    sub_category = models.CharField(max_length=100, null=False)
    # name = models.CharField(max_length=100, null=False)
    make = models.CharField(max_length=100, null=False)
    model = models.CharField(max_length=100, null=False)
    serial_number = models.CharField(max_length=50, unique=True, null=False)

    price = models.DecimalField(default= 0.0 ,null=True, decimal_places=2,max_digits=9)
    order = models.ForeignKey('orders.Order',on_delete=models.SET_NULL,null=True,blank=True)

    receipt_date = models.DateTimeField(null=True, blank=True)
    warranty_expiration = models.DateTimeField(null=True, blank=True)

    # Dynamically set choices in a custom method
    def get_status_choices():
        return [(status.status_values, status.status_values) for status in  Status.get_status_values()]
        #return Status.get_status_values()

    def get_condition_choices():
        return [(condition.condition_values, condition.condition_values) for condition in Condition.get_condition_values()]
        #return Condition.get_condition_values()
    

    status = models.CharField(max_length=20,default="AVAILABLE",choices=get_status_choices)
    condition = models.CharField(max_length=40,default="NEW & WORKING",choices=get_condition_choices)
    # location = models.CharField(max_length=100, blank=True, null=True)
    assignment_id = models.PositiveIntegerField(null=True)
    notes = models.TextField(blank=True,null=True)
    
    created_by = models.CharField(max_length=100, null=False)
    created_on = models.DateTimeField(default=timezone.now)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.name} - {self.serial_number}'


