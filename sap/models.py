"""Contains all the table definitions of the project."""
from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.

# Need to figure out how to include the following
# Are you interested in serving as a mentor to students who identify as any of the following (check all that may apply)
class Ally(models.Model):
    """
    Ally model contains the details of the IBA allies
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    hawk_id = models.CharField(max_length=100)
    image_url = models.CharField(max_length=500,
                                 default="https://sepibafiles.blob.core.windows.net/sepibacontainer/blank-profile-picture.png")
    user_type = models.CharField(max_length=25)  # student/faculty/..

    ## Additional authentication fields
    reset_password = models.BooleanField(default=False)

    def __str__(self):
        return self.hawk_id

    ##Grad and Faculty
    area_of_research = models.CharField(max_length=500, null=True)
    openings_in_lab_serving_at = models.BooleanField(default=False)
    description_of_research_done_at_lab = models.CharField(max_length=500, null=True)
    interested_in_mentoring = models.BooleanField(default=False)
    interested_in_mentor_training = models.BooleanField(default=False)
    willing_to_offer_lab_shadowing = models.BooleanField(default=False)
    interested_in_connecting_with_other_mentors = models.BooleanField(default=False)
    willing_to_volunteer_for_events = models.BooleanField(default=False)
    works_at = models.CharField(max_length=200, null=True)

    ##Staff
    people_who_might_be_interested_in_iba = models.BooleanField(default=False)
    how_can_science_ally_serve_you = models.CharField(max_length=500, null=True)

    ##Undergraduate
    year = models.CharField(max_length=30)
    major = models.CharField(max_length=50)
    information_release = models.BooleanField(default=False)
    interested_in_being_mentored = models.BooleanField(default=False)
    identity = models.CharField(max_length=200, blank=True)
    interested_in_joining_lab = models.BooleanField(default=False)
    has_lab_experience = models.BooleanField(default=False)

class AllyMentorRelation(models.Model):
    """
    AllyMentorRelation table is used for mapping One to One relationship between allies and their mentors
    """
    ally = models.OneToOneField(
        Ally,
        related_name='ally_mentor_relation',
        on_delete=models.CASCADE,
    )
    mentor = models.ForeignKey(
        Ally,
        related_name='mentor',
        on_delete=models.CASCADE,
    )

class AllyMenteeRelation(models.Model):
    """
    AllyMenteeRelation table is used for mapping One to Manu relationship between allies and their mentee
    """
    ally = models.ForeignKey(
        Ally,
        related_name='ally_mentee_relation',
        on_delete=models.CASCADE,
    )
    mentee = models.ForeignKey(
        Ally,
        related_name='mentee',
        on_delete=models.CASCADE,
    )

class StudentCategories(models.Model):
    """
    StudentCategories table contains the different special cateories an uiowa student can belong to
    """
    under_represented_racial_ethnic = models.BooleanField(default=False)
    first_gen_college_student = models.BooleanField(default=False)
    transfer_student = models.BooleanField(default=False)
    lgbtq = models.BooleanField(default=False)
    low_income = models.BooleanField(default=False)
    rural = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)


class AllyStudentCategoryRelation(models.Model):
    """
    AllyStudentCategoryRelation table is used for mapping Many to Many relationship between allies and StudentCategories table
    """
    ally = models.ForeignKey(
        Ally,
        on_delete=models.CASCADE,
    )
    student_category = models.ForeignKey(
        StudentCategories,
        on_delete=models.CASCADE,
    )


class Event(models.Model):
    """
    Evert table contains information about the IBA science alliance events
    """
    title = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=1000, null=True)
    start_time = models.DateTimeField(default=None, null=True)
    end_time = models.DateTimeField(default=None, null=True)
    allday = models.CharField(max_length=500, null=True)
    location = models.CharField(max_length=500, null=True)
    num_invited = models.IntegerField(default=0)
    num_attending = models.IntegerField(default=0)
    role_selected = models.CharField(max_length=500, null=True)
    school_year_selected = models.CharField(max_length=500, null=True)
    mentor_status = models.CharField(max_length=500, null=True)
    research_field = models.CharField(max_length=500, null=True)
    invite_all = models.CharField(max_length=500, null=True)
    special_category = models.CharField(max_length=500, null=True)


class EventInviteeRelation(models.Model):
    """
    EventAllyRelation table contains information about the Event ally mappings
    One event can have many allies invited and vice versa
    """
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE
                              )
    ally = models.ForeignKey(Ally,
                             on_delete=models.CASCADE
                             )


class Announcement(models.Model):
    """
    Announcement table contains information about the announcemernts made by admin
    """
    username = models.CharField(max_length=100)
    title = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=1000, null=True)
    created_at = models.DateTimeField()


class EventAttendeeRelation(models.Model):
    """
    EventAttendeeRelation table contains information about the Event ally mappings
    One event can have many allies registered and vice versa
    """
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE
                              )
    ally = models.ForeignKey(Ally,
                             on_delete=models.CASCADE
                             )
