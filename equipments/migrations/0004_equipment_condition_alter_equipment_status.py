# Generated by Django 5.0.4 on 2024-09-07 12:10

import miscellaneous.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipments', '0003_remove_equipment_assigned_to_equipment_assignment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='condition',
            field=models.CharField(choices=miscellaneous.models.Condition.get_condition_values, default='NEW & WORKING', max_length=40),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='status',
            field=models.CharField(choices=miscellaneous.models.Status.get_status_values, default='AVAILABLE', max_length=20),
        ),
    ]
