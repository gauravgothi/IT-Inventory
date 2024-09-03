from django.db import models
from django.contrib.auth.models import User

class Assignee(models.Model):
    id = models.AutoField(primary_key=True)
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    type_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.type_code}"
