# Generated by Django 3.1 on 2021-05-05 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sap', '0020_allymenteerelation_allymentorrelation'),
    ]

    operations = [
        migrations.AddField(
            model_name='ally',
            name='reset_password',
            field=models.BooleanField(default=False),
        ),
    ]
