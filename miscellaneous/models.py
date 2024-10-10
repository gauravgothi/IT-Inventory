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
    
class CategorySubcategory(models.Model):
    id = models.AutoField(primary_key=True)

    category = models.CharField(max_length=50,null=False)
    subcategory = models.CharField(max_length=60,null=False)

    @classmethod
    def get_categories(cls):
        return list(cls.objects.values_list('category', flat=True).distinct())
    
    @classmethod
    def get_subcategories(cls,category):
        return list(cls.objects.filter(category=category).values_list('subcategory',flat=True).distinct())

    def __str__(self):
        return f'{self.category} - {self.subcategory}'
    

