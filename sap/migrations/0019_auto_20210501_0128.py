# Generated by Django 3.1 on 2021-05-01 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sap', '0018_merge_20210430_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='allday',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='invite_all',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
