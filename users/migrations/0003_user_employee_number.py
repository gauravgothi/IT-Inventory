# Generated by Django 5.0.4 on 2024-09-09 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_office_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='employee_number',
            field=models.CharField(max_length=11, null=True),
        ),
    ]
