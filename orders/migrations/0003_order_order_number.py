# Generated by Django 5.0.4 on 2024-09-25 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_po_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
