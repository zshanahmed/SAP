# Generated by Django 3.1 on 2021-03-09 23:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ally',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hawk_id', models.CharField(max_length=100)),
                ('user_type', models.CharField(max_length=20)),
                ('area_of_research', models.CharField(max_length=200, null=True)),
                ('openings_in_lab_serving_at', models.BooleanField(default=False)),
                ('description_of_research_done_at_lab', models.CharField(max_length=500, null=True)),
                ('interested_in_mentoring', models.BooleanField(default=False)),
                ('interested_in_mentor_training', models.BooleanField(default=False)),
                ('willing_to_offer_lab_shadowing', models.BooleanField(default=False)),
                ('interested_in_connecting_with_other_mentors', models.BooleanField(default=False)),
                ('willing_to_volunteer_for_events', models.BooleanField(default=False)),
                ('works_at', models.CharField(max_length=200, null=True)),
                ('people_who_might_be_interested_in_iba', models.BooleanField(default=False)),
                ('how_can_science_ally_serve_you', models.CharField(max_length=500, null=True)),
                ('year', models.CharField(max_length=30)),
                ('major', models.CharField(max_length=50)),
                ('information_release', models.BooleanField(default=False)),
                ('interested_in_being_mentored', models.BooleanField(default=False)),
                ('identity', models.CharField(blank=True, max_length=200)),
                ('interested_in_joining_lab', models.BooleanField(default=False)),
                ('has_lab_experience', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentCategories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('under_represented_racial_ethnic', models.BooleanField(default=False)),
                ('first_gen_college_student', models.BooleanField(default=False)),
                ('transfer_student', models.BooleanField(default=False)),
                ('lgbtq', models.BooleanField(default=False)),
                ('low_income', models.BooleanField(default=False)),
                ('rural', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AllyStudentCategoryRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ally', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sap.ally')),
                ('student_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sap.studentcategories')),
            ],
        ),
    ]
