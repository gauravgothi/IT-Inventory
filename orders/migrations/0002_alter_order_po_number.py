# Generated by Django 5.0.4 on 2024-09-03 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='po_number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
