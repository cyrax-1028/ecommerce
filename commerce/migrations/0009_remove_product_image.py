# Generated by Django 5.1.5 on 2025-02-15 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0008_rename_tax_order_tax_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
