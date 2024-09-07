from django.db import models

class Location(models.Model):
    location_code = models.PositiveIntegerField(primary_key=True)
    location_name = models.CharField(max_length=255, null=False)
    division_code = models.PositiveIntegerField(null=True, blank=True)
    division_name = models.CharField(max_length=255, null=True, blank=True)
    circle_code = models.PositiveIntegerField(null=True, blank=True)
    circle_name = models.CharField(max_length=255, null=True, blank=True)
    region_code = models.PositiveIntegerField(null=True, blank=True)
    region_name = models.CharField(max_length=255, null=True, blank=True)
    org_code = models.PositiveIntegerField(null=True, blank=True)  # Code fields as positive integers
    org_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.location_name 
    
class Employee(models.Model):
    employee_number = models.PositiveIntegerField(primary_key=True)
    user_person_type = models.CharField(max_length=50, null=True, blank=True)
    employee_name = models.CharField(max_length=255, null=False) 
    date_of_birth = models.DateField(null=True, blank=True)
    original_date_of_hire = models.DateField(null=True, blank=True)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    email_address = models.EmailField(max_length=255, null=True, blank=True)  
    designation = models.CharField(max_length=100, null=True, blank=True)
    grade = models.CharField(max_length=50, null=True, blank=True)
    office = models.CharField(max_length=255, null=True, blank=True)
    work_location = models.CharField(max_length=255, null=True, blank=True)
    emp_class = models.CharField(max_length=50, null=True, blank=True)
    tech_nontech = models.CharField(max_length=50, null=True, blank=True)
    oic_no = models.PositiveIntegerField(null=True, blank=True)
    oic_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.employee_name

class Vendor(models.Model):
    vendor_code = models.PositiveIntegerField(primary_key=True)
    vendor_name = models.CharField(max_length=255,null=False)  

    def __str__(self):
        return self.vendor_name

class Assignee:
    def __init__(self, target_type:str, target_code:any):
        self.target_type = target_type.lower()
        self.target_code = target_code

    def __str__(self):
        return f"{self.target_type} - {self.target_code}"
    

