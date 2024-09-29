from datetime import timezone
from django.db import models
from django.forms import ValidationError

from assignees.models import Assignee
from miscellaneous.models import Condition
from equipments.models import Equipment

class Assignment(models.Model):
    @staticmethod
    def get_condition_choices():
        return [(condition.condition_values, condition.condition_values) for condition in Condition.get_condition_values()]
        #return Condition.get_condition_values()

    id = models.AutoField(primary_key=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE,null=False)
    assigned_to = models.PositiveIntegerField(null=True)
    assigned_to_details = models.TextField(blank=False, null=False)
    assigned_type = models.CharField(max_length=20,null=True)
    assigned_date = models.DateTimeField(null=False)
    letter_for_issue = models.CharField(max_length=200,null=True,blank=True)
    return_date = models.DateTimeField(null=True)
    assigned_condition = models.CharField(max_length=20,default=None,choices=get_condition_choices,null=True)
    issue_person_name = models.CharField(max_length=100,null=True,blank=False)
    issue_person_code = models.CharField(max_length=20,null=True,blank=False)
    returned_condition = models.CharField(max_length=20,default=None,choices=get_condition_choices,null=True)
    letter_for_return = models.CharField(max_length=200,null=True,blank=True)
    return_person_name = models.CharField(max_length=100,null=True,blank=False)
    return_person_code = models.CharField(max_length=20,null=True,blank=False)
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(null=False,blank=False)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    updated_on = models.DateTimeField(null=True)

    @classmethod
    def get_assignment_history(cls, equipment_id):
        return cls.objects.filter(equipment_id=equipment_id).order_by('id')

    def __str__(self):
        return f"equipment {self.equipment.serial_number} assigned to {self.assigned_to}, {self.assigned_to_details} on {self.assigned_date}"
