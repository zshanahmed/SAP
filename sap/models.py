from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# Need to figure out how to include the following
# Are you interested in serving as a mentor to students who identify as any of the following (check all that may apply)

Roles = (
    ('admin', 'ADMIN'),
    ('ally', 'ALLY'),

)

class Ally(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    hawk_id = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=Roles, default='admin')  # student/faculty/..
    works_at = models.CharField(max_length=100)  # college_of_engineering / college of liberal arts

    def __str__(self):
        return self.user.username

    area_of_research = models.CharField(max_length=100, null=True)
    openings_in_lab_serving_at = models.BooleanField(default=False)
    description_of_research_done_at_lab = models.CharField(max_length=500, null=True)
    interested_in_mentoring = models.BooleanField(default=False)
    willing_to_offer_lab_shadowing = models.BooleanField(default=False)
    interested_in_connecting_with_other_mentors = models.BooleanField(default=False)
    willing_to_volunteer_for_events = models.BooleanField(default=False)
    interested_in_being_mentored = models.BooleanField(default=False)
    people_who_might_be_interested_in_iba = models.CharField(max_length=500, default='')
    how_can_science_ally_serve_you = models.CharField(max_length=500, null=True)
    year = models.CharField(max_length=30)
    major = models.CharField(max_length=50)
    interested_in_joining_lab = models.BooleanField(default=False)
    has_lab_experience = models.BooleanField(default=False)
    interested_in_peer_mentoring = models.BooleanField(default=False)


class StudentCategories(models.Model):
    under_represented_racial_ethnic = models.BooleanField(default=False)
    first_gen_college_student = models.BooleanField(default=False)
    transfer_student = models.BooleanField(default=False)
    lbgtq = models.BooleanField(default=False)


class AllyStudentCategoryRelation(models.Model):
    ally = models.ForeignKey(
        Ally,
        on_delete=models.CASCADE,
    )
    student_category = models.ForeignKey(
        StudentCategories,
        on_delete=models.CASCADE,
    )
