from datetime import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    #Default field by AbstractUser
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128,null=False)

    #Additional Fields
    role = models.CharField(max_length=50,null=False) 
    status = models.CharField(max_length=50, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    email = models.EmailField(max_length=254) 
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    created_by = models.CharField(max_length=150)
    updated_by = models.CharField(max_length=150)
    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
