# Generated by Django 3.1 on 2021-03-29 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sap', '0009_auto_20210324_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentcategories',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]
