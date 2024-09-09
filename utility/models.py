from datetime import datetime, timedelta, timezone
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

class IssueSlip:
    def __init__(self, item_name=None, gen_date=None, serial_number=None, remark=None,rec_emp_num=None,rec_emp_name=None,rec_office=None,iss_emp_num=None,iss_emp_name=None,iss_office=None):
        indian_time = timezone(timedelta(hours=5, minutes=30))
        self.item_name = item_name
        self.gen_date = gen_date
        self.serial_number = serial_number
        self.remark = remark
        self.rec_emp_num = rec_emp_num
        self.rec_emp_name = rec_emp_name
        self.rec_office = rec_office
        self.iss_emp_num = iss_emp_num
        self.iss_emp_name = iss_emp_name
        self.iss_office = iss_office

        

    def set_item_name(self, item_name):
        self.item_name = item_name

    def set_gen_date(self, gen_date):
        self.gen_date = gen_date

    def set_serial_number(self, serial_number):
        self.serial_number = serial_number

    def set_remark(self, remark):
        self.remark = remark

    def set_rec_emp_num(self, rec_emp_num):
        self.rec_emp_num = rec_emp_num

    def set_rec_emp_name(self, rec_emp_name):
        self.rec_emp_name = rec_emp_name

    def set_rec_office(self, rec_office):
        self.rec_office = rec_office

    def set_iss_emp_num(self, iss_emp_num):
        self.iss_emp_num = iss_emp_num

    def set_iss_emp_name(self, iss_emp_name):
        self.iss_emp_name = iss_emp_name

    def set_iss_office(self, iss_office):
        self.iss_office = iss_office



