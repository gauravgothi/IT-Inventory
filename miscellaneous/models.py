# models.py in miscellaneous app
from django.db import models

class Status(models.Model):
    status_values = models.CharField(max_length=20, primary_key=True)

    @staticmethod
    def get_status_values():
        #return [(status.status_values, status.status_values) for status in Status.objects.all()]
        return Status.objects.all()

class Condition(models.Model):
    condition_values = models.CharField(max_length=40, primary_key=True)

    @staticmethod
    def get_condition_values():
        #return [(condition.condition_values, condition.condition_values) for condition in Condition.objects.all()]
        return Condition.objects.all()
