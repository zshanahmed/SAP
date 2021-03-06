# Generated by Django 3.1 on 2021-04-09 21:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sap', '0010_studentcategories_disabled'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EventAllyRelation',
            new_name='EventAttendeeRelation',
        ),
        migrations.RemoveField(
            model_name='event',
            name='datetime',
        ),
        migrations.AddField(
            model_name='event',
            name='allday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='end_time',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.CreateModel(
            name='EventInviteeRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ally', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sap.ally')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sap.event')),
            ],
        ),
    ]
