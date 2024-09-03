from datetime import timezone
from django.db import models

from assignees.models import Assignee
from equipments.models import Equipment

class Assignment(models.Model):
    ASSIGNED_CONDITION_CHOICES = [
        ('NEW', 'NEW'),
        ('GOOD', 'GOOD'),
        ('FAIR', 'FAIR'),
        ('POOR', 'POOR'),
    ]

    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE,null=False)
    assigned_to = models.ForeignKey(Assignee, on_delete=models.SET_NULL,null=True)
    assigned_type = models.CharField(max_length=20,null=False)
    assigned_date = models.DateTimeField(null=False)
    return_date = models.DateTimeField(null=True, blank=True)
    assigned_condition = models.CharField(max_length=20, choices=ASSIGNED_CONDITION_CHOICES)
    returned_condition = models.CharField(max_length=20, choices=ASSIGNED_CONDITION_CHOICES, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(null=False,blank=False)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.equipment.name} assigned to {self.assigned_to} on {self.assigned_date}"
