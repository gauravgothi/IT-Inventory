# Generated by Django 5.0.4 on 2024-09-05 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0002_alter_assignment_letter_for_issue_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='assigned_to',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='assigned_type',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
