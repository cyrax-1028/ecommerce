# Generated by Django 5.1.5 on 2025-02-06 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0002_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
