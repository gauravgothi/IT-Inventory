from datetime import timezone
from django.db import models

from assignees.models import Assignee
from miscellaneous.models import Condition
from equipments.models import Equipment

class Assignment(models.Model):
    def get_condition_choices():
        return [(condition.condition_values, condition.condition_values) for condition in Condition.get_condition_values()]
        #return Condition.get_condition_values()

    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE,null=False)
    assigned_to = models.PositiveIntegerField(null=True)
    assigned_type = models.CharField(max_length=20,null=True)
    assigned_date = models.DateTimeField(null=False)
    letter_for_issue = models.CharField(max_length=200,null=True,blank=True)
    return_date = models.DateTimeField(null=True)
    assigned_condition = models.CharField(max_length=20,default="NEW & WORKING",choices=get_condition_choices)
    returned_condition = models.CharField(max_length=20,default="OLD & WORKING",choices=get_condition_choices)
    letter_for_return = models.CharField(max_length=200,null=True,blank=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(null=False,blank=False)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.equipment.name} assigned to {self.assigned_to} on {self.assigned_date}"
