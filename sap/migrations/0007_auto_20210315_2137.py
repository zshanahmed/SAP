# Generated by Django 3.1 on 2021-03-15 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sap', '0006_auto_20210306_0144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ally',
            name='user_type',
            field=models.CharField(max_length=25),
        ),
    ]
