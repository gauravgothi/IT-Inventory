from django.db import models

# Model to store PDF and JPG files
class Document(models.Model):
    file = models.FileField(upload_to='documents/')

# Model to store Excel, XLS, and CSV files
class Spreadsheet(models.Model):
    file = models.FileField(upload_to='spreadsheets/')

class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)



