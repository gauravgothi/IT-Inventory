# Generated by Django 5.0.4 on 2024-09-07 15:13

import assignments.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0003_alter_assignment_assigned_to_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_condition',
            field=models.CharField(choices=assignments.models.Assignment.get_condition_choices, default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='returned_condition',
            field=models.CharField(choices=assignments.models.Assignment.get_condition_choices, default=None, max_length=20, null=True),
        ),
    ]
