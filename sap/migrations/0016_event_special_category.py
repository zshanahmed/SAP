# Generated by Django 3.1 on 2021-04-19 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sap', '0015_event_invite_all'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='special_category',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
