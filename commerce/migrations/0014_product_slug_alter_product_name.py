# Generated by Django 5.1.5 on 2025-02-26 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commerce', '0013_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
