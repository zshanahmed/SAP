"""
contains unit tests for sap app
"""

from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, EventInviteeRelation

# Create your tests here.
from .tokens import account_activation_token

User = get_user_model()

class SignUpTests(TestCase):
    """
    Testing all different scenarios of signup for different types of users
    """

    def setUp(self):
        self.username = 'admin2'
        self.username_active = 'user_active2'
        self.password = 'admin_password21'
        self.email = 'email2@test.com'
        self.email_active = 'email_active2@test.com'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.user_active = User.objects.create_user(username=self.username_active, email=self.email_active, password=self.password,
                                                    is_active=True)
        self.client = Client()

        self.another_username = 'another_username'
        self.another_email = 'another_email@uiowa.edu'

    def test_get_success(self):
        """
        Can access if user is not logged in.
        """
        self.client.logout()
        response = self.client.get('/sign-up/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_fail(self):
        """
        Sign-up page exists.
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/sign-up/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_entered_existing_active_emailaddress(self):
        """
        Cannot create new account if enter known email address and its is_active=True.
        """
        self.user.is_active = True
        self.user.save()
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': ['admin1'],
                'new_email': self.user.email,
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student'],
                'labShadowRadios': ['Yes'],
                'connectingWithMentorsRadios': ['Yes'],
                'volunteerRadios': ['Yes'],
                'trainingRadios': ['Yes'],
                'howCanWeHelp': ['123'],
                'research-des': [''],
                'openingRadios': ['Yes'],
                'studentsInterestedRadios': ['Yes']
            }
        )
        self.assertEqual(response.url, '/sign-up')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_entered_existing_inactive_email_address(self):
        """
        If user enters inactive email address.
        All other requirement satisfies.
        A new account for that inactive email address can be created.
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': self.user.username,
                'new_email': self.user.email,
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student',
                                     'Underrepresented racial/ethnic minority',
                                     'LGBTQ', 'Rural', 'Disabled'],
                'labShadowRadios': ['Yes'],
                'connectingWithMentorsRadios': ['Yes'],
                'volunteerRadios': ['Yes'],
                'trainingRadios': ['Yes'],
                'howCanWeHelp': ['123'],
                'research-des': [''],
                'openingRadios': ['Yes'],
                'studentsInterestedRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(self.user.is_active, False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_entered_existing_inactive_email_address_existing_username(self):
        """
        If user enters inactive email address.
        However existing username is entered.
        A new account for that inactive email address cannot be created.
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': self.user_active.username,
                'new_email': self.user.email,
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student'],
                'labShadowRadios': ['Yes'],
                'connectingWithMentorsRadios': ['Yes'],
                'volunteerRadios': ['Yes'],
                'trainingRadios': ['Yes'],
                'howCanWeHelp': ['123'],
                'research-des': [''],
                'openingRadios': ['Yes'],
                'studentsInterestedRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(self.user.is_active, False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_entered_existing_inactive_email_address_mismatched_password(self):
        """
        If user enters inactive email address.
        However mismatched passwords are entered.
        A new account for that inactive email address cannot be created.
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': self.another_username,
                'new_email': self.user.email,
                'new_password': self.password,
                'repeat_password': 'as;dlfja;lsdjf;alksdjf;lkjZSDKjf;k',
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student'],
                'labShadowRadios': ['Yes'],
                'connectingWithMentorsRadios': ['Yes'],
                'volunteerRadios': ['Yes'],
                'trainingRadios': ['Yes'],
                'howCanWeHelp': ['1234'],
                'research-des': [''],
                'openingRadios': ['Yes'],
                'studentsInterestedRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(self.user.is_active, False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_entered_existing_inactive_email_address_bad_password(self):
        """
        If user enters inactive email address.
        However new pass < 8 chars.
        A new account for that inactive email address cannot be created.
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': self.another_username,
                'new_email': self.user.email,
                'new_password': 'big',
                'repeat_password': 'big',
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student'],
                'labShadowRadios': ['Yes'],
                'connectingWithMentorsRadios': ['Yes'],
                'volunteerRadios': ['Yes'],
                'trainingRadios': ['Yes'],
                'howCanWeHelp': ['1234'],
                'research-des': [''],
                'openingRadios': ['Yes'],
                'studentsInterestedRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(self.user.is_active, False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_entered_unknown_email_address_existing_username(self):
        """
        test with a valid username but with an invalid email address
        """
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': self.user.username,
                'new_email': self.another_email,
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student'],
                'labShadowRadios': ['Yes'],
                'connectingWithMentorsRadios': ['Yes'],
                'volunteerRadios': ['Yes'],
                'trainingRadios': ['Yes'],
                'howCanWeHelp': ['1234'],
                'research-des': [''],
                'openingRadios': ['Yes'],
                'studentsInterestedRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_password_not_same(self):
        """
        test if password and confirm password fields have the same value
        """
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                'firstName': ['Elias'],
                'lastName': ['Shaeffer'],
                'new_username': ['admin1123'],
                'new_email': ['email123@test.com'],
                'new_password': self.password,
                'repeat_password': ['ddddd'],
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Biochemistry'],
                'mentoringRadios': ['Yes'],
                'mentorCheckboxes': ['First generation college-student'],
                'labShadowRadios': ['Yes'],
                'connectingRadios': ['Yes'],
                'volunteerGradRadios': ['Yes'],
                'trainingRadios': ['Yes'],
            }
        )
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_create_undergrad(self):
        """
        Test signup feature using undergrad user interested in being mentored
        """
        event = Event.objects.create(
            title="Mock Interviews",
            description="This event is for mock interviews",
            location="Maclean Hall",
            allday=False,
            end_time="2021-05-02 22:19:00",
            start_time="2021-05-02 21:19:00",
            num_attending=0,
            num_invited=0,
            mentor_status="Mentees",
            research_field="Computer Science and Engineering",
            role_selected="Undergraduate Student",
            school_year_selected="Freshman",
            invite_all=False
        )
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                'firstName': ['Zeeshan'],
                'lastName': ['Ahmed'],
                'new_username': ['zeeahmed1'],
                'new_email': ['zeeahmed@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Undergraduate Student'], 'undergradYear': ['Freshman'],
              'identityCheckboxes': ['First generation college-student'], 'major': ['major'],
              'interestLabRadios': ['Yes'], 'labExperienceRadios': ['Yes'],
              'undergradMentoringRadios': ['Yes'], 'beingMentoredRadios': ['Yes'], 'agreementRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed1")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        invitation = EventInviteeRelation.objects.filter(ally_id=ally[0].id, event_id=event.id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(invitation.exists())
        Event.objects.get(pk=event.id).delete()
        self.assertTrue(categories.exists())
        Event.objects.create(
            title="Mock Interviews",
            description="This event is for mock interviews",
            location="Maclean Hall",
            allday=False,
            invite_all=False,
            end_time="2021-05-06 22:19:00",
            start_time="2021-05-02 21:19:00",
            role_selected="Graduate Student,Undergraduate Student",
            school_year_selected="Freshman"
        )
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                'firstName': ['Zeeshan'],
                'lastName': ['Ahmed'],
                'new_username': ['zeeahmed1'],
                'new_email': ['zeeahmed@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Undergraduate Student'], 'undergradYear': ['Freshman'],
                'major': ['major'],
                'interestLabRadios': ['Yes'], 'labExperienceRadios': ['Yes'],
                'undergradMentoringRadios': ['Yes'], 'beingMentoredRadios': ['Yes'], 'agreementRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed1")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        invitation = EventInviteeRelation.objects.filter(ally_id=ally[0].id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(invitation.exists())
        self.assertTrue(categories.exists())

    def test_create_undergrad_non_mentees(self):
        """
        Test signup feature using undergrad user not interested in being mentored
        """
        Event.objects.create(
            title="Mock Interviews",
            description="This event is for mock interviews",
            location="Maclean Hall",
            allday=False,
            invite_all=False,
            end_time="2021-05-06 22:19:00",
            start_time="2021-05-02 21:19:00",
            role_selected="Graduate Student,Undergraduate Student",
            school_year_selected="Freshman"
        )
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                'firstName': ['Zeeshan'],
                'lastName': ['Ahmed'],
                'new_username': ['zeeahmed1'],
                'new_email': ['zeeahmed@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Undergraduate Student'], 'undergradYear': ['Freshman'],
              'identityCheckboxes': ['First generation college-student'], 'major': ['major'],
              'interestLabRadios': ['Yes'], 'labExperienceRadios': ['Yes'],
              'undergradMentoringRadios': ['No'], 'beingMentoredRadios': ['No'], 'agreementRadios': ['Yes']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed1")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        event_invitee = Event.objects.filter(role_selected__contains='Undergraduate Student').filter(
                                            school_year_selected__contains='Freshman')
        invitation = EventInviteeRelation.objects.filter(ally_id=ally[0].id, event_id=event_invitee[0].id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertEqual(ally[0].interested_in_being_mentored, False)
        self.assertTrue(invitation.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(categories.exists())

    def test_create_grad(self):
        """
        Test signup feature using a grad user
        """
        event = Event.objects.create(
                                          title="Mock Interviews",
                                          description="This event is for mock interviews",
                                          location="Maclean Hall",
                                          allday=False,
                                          end_time="2021-05-02 22:19:00",
                                          start_time="2021-05-02 21:19:00",
                                          num_attending=0,
                                          num_invited=0,
                                          mentor_status="Mentors,Mentees",
                                          research_field="Computer Science and Engineering",
                                          role_selected="Graduate Student,Undergraduate Student",
                                          special_category="First generation college-student",
                                          invite_all=False
                                          )
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'],
                'firstName': ['glumpy'],
                'lastName': ['guy'],
                'new_username': ['big_guy1'],
                'new_email': ['eshaeffer@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Computer Science and Engineering'], 'research-des': ['research'],
                'openingRadios': ['No'], 'mentoringRadios': ['Yes'], 'connectingWithMentorsRadios': ['Yes'],
                'studentsInterestedRadios': ['No'], 'mentorCheckboxes': ['Low-income'], 'labShadowRadios': ['Yes'],
                'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes'], 'howCanWeHelp': ['no']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy1")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        invitation = EventInviteeRelation.objects.filter(ally_id=ally[0].id, event_id=event.id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(invitation.exists())
        self.assertTrue(categories.exists())

    def test_create_grad_no_mentor_events(self):
        """
        Test signup feature using a grad user with no events having mentors
        """
        event1 = Event.objects.create(
            title="Mock Interviews",
            description="This event is for mock interviews",
            location="Maclean Hall",
            allday=False,
            invite_all=False,
            end_time="2021-05-06 22:19:00",
            start_time="2021-05-02 21:19:00",
            role_selected="Graduate Student,Undergraduate Student",
            school_year_selected="Freshman"
        )
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['nl8oQ7HV6N0vEI7lWN9ji8Ehw38tcKRDb9MQrJfuh4VChgEF8UCS3anXIoHKBro7'],
                 'firstName': ['Zeeshan'], 'lastName': ['Ahmed'],
                 'new_username': ['zeeahmed'], 'new_email': ['zeeshan-ahmed@uiowa.edu'],
                 'new_password': [self.password], 'repeat_password': [self.password],
                 'roleSelected': ['Graduate Student'], 'research-des': ['LTE Security'],
                 'openingRadios': ['No'], 'mentoringRadios': ['Yes'], 'connectingWithMentorsRadios': ['No'],
                 'studentsInterestedRadios': ['No'], 'labShadowRadios': ['No'], 'volunteerRadios': ['No'],
                 'trainingRadios': ['No'], 'howCanWeHelp': ['Internship']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user1 = User.objects.filter(username="zeeahmed")
        ally1 = Ally.objects.filter(user_id=user1[0].id)
        self.assertTrue(EventInviteeRelation.objects.filter(ally_id=ally1[0].id, event_id=event1.id).exists())
        self.assertTrue(ally1.exists())
        self.assertTrue(user1.exists())

    def test_create_grad_non_mentors(self):
        """
        Test signup feature using a grad user non mentors
        """
        Event.objects.create(
            title="Mock Interviews",
            description="This event is for mock interviews",
            location="Maclean Hall",
            allday=False,
            invite_all=False,
            end_time="2021-05-06 22:19:00",
            start_time="2021-05-02 21:19:00",
            role_selected="Graduate Student,Undergraduate Student",
            school_year_selected="Freshman"
        )
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'],
                'firstName': ['glumpy'],
                'lastName': ['guy'],
                'new_username': ['big_guy1'],
                'new_email': ['eshaeffer@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'areaOfResearchCheckboxes': ['Computer Science and Engineering'], 'research-des': ['research'],
                'openingRadios': ['No'], 'mentoringRadios': ['No'], 'connectingWithMentorsRadios': ['No'],
                'studentsInterestedRadios': ['No'], 'mentorCheckboxes': ['Low-income'], 'labShadowRadios': ['No'],
                'volunteerRadios': ['No'], 'trainingRadios': ['No'], 'howCanWeHelp': ['No']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy1")
        ally = Ally.objects.filter(user_id=user[0].id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertFalse(ally[0].interested_in_mentoring)
        grad_event = Event.objects.filter(role_selected__contains='Graduate Student')
        invitation2 = EventInviteeRelation.objects.filter(ally_id=ally[0].id, event_id=grad_event[0].id)
        self.assertTrue(invitation2.exists())

    def test_create_grad_no_boxes(self):
        """
        Test grad signup with a specific configuration
        """
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'],
                'firstName': ['glumpy'],
                'lastName': ['guy'],
                'new_username': ['big_guy12'],
                'new_email': ['eshaeffer@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'research-des': ['research'],
                'openingRadios': ['No'], 'mentoringRadios': ['No'], 'connectingWithMentorsRadios': ['Yes'],
                'studentsInterestedRadios': ['No'], 'labShadowRadios': ['Yes'],
                'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes'], 'howCanWeHelp': ['no']
            }
        )
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy12")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(categories.exists())

    def test_password_less_than_minimum(self):
        """
        unit test for minimum password requirement
        """
        response = self.client.post(
            "/sign-up/",
            {
                "csrfmiddlewaretoken": ["K5dFCUih0K6ZYklAemhvIWSpCebK86zdx4ric6ucIPLUQhAdtdT7hhp4r5etxoJY"],
                "firstName": ["hawk"],
                "lastName": ["herky"],
                "new_username": ["hawkherkydiff"],
                "new_email": ["hawkherkydiff@uiowa.edu"],
                "new_password": ["ddd"],
                "repeat_password": ["ddd"],
                "roleSelected": ["Staff"],
                "studentsInterestedRadios": ["Yes"],
                "howCanWeHelp": ["sasdasdasd"],
            },
        )
        url = response.url
        self.assertEqual(url, "/sign-up")
        self.assertEqual(response.status_code, 302)


    def test_signup_confirm_success(self):
        """
        The unique link to activate password exists and works
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()

        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:sign-up-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.FOUND)

    def test_signup_confirm_active_user(self):
        """
        User is already active.
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()

        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:sign-up-confirm', args=[uid, token])

        self.user.is_active = True
        self.user.save()

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.FOUND)

    def test_signup_confirm_invalid(self):
        """
        Invalid activation link.
        """
        self.user.is_active = False
        Ally.objects.create(user=self.user,
                            user_type=['Graduate Student'],
                            hawk_id=self.user.username,
                            area_of_research=['Biochemistry'],
                            interested_in_mentoring=False,
                            willing_to_offer_lab_shadowing=False,
                            interested_in_connecting_with_other_mentors=False,
                            willing_to_volunteer_for_events=False,
                            interested_in_mentor_training=True)
        self.user.save()
        self.client.logout()

        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:sign-up-confirm', args=[uid, token])

        self.user.delete()

        self.user.is_active = True
        self.user.save()

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.FOUND)

# class SignUpDoneViewTests(TestCase):
#     """
#     Unit tests for SignUpDoneView
#     """
#     def setUp(self):
#         self.username = 'admin1'
#         self.username_active = 'user_active1'
#         self.password = 'admin_password12'
#         self.email = 'email1@test.com'
#         self.active_email = 'email_active1@test.com'
#         self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
#         self.user_active = User.objects.create_user(username=self.username_active, email=self.active_email,
#                                                     password=self.password,
#                                                     is_active=True)
#         self.client = Client()
#
#     def test_if_user_come_from_signup(self):
#         """
#         If user comes from sign-up, redirect to the page
#         """
#         response = self.client.post(
#             '/sign-up/',
#             {
#                 'csrfmiddlewaretoken': ['K5dFCUih0K6ZYklAemhvIWSpCebK86zdx4ric6ucIPLUQhAdtdT7hhp4r5etxoJY'],
#                 'firstName': ['hawk'],
#                 'lastName': ['herky'],
#                 'new_username': ['hawkherky'],
#                 'new_email': ['hawkherky@uiowa.edu'],
#                 'new_password': self.password,
#                 'repeat_password': self.password,
#                 'roleSelected': ['Graduate Student'],
#                 'research-des': ['research'],
#                 'openingRadios': ['No'], 'mentoringRadios': ['No'], 'connectingWithMentorsRadios': ['Yes'],
#                 'studentsInterestedRadios': ['No'], 'labShadowRadios': ['Yes'],
#                 'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes'], 'howCanWeHelp': ['no']
#             }
#         )
#
#         # response2 = response
#         url = response.url
#         self.assertEqual(url, '/sign-up-done/')
#         self.assertEqual(response.status_code, 302)
#
#     def test_signup_if_user_is_authenticated(self):
#         """
#         If user is authenticated
#         """
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('sap:sign-up-done'))
#         self.assertEqual(response.status_code, 302)
#
#     def test_signup_if_keyerror(self):
#         """
#         If keyerror
#         """
#         self.client.logout()
#         response = self.client.get(reverse('sap:sign-up-done'))
#         self.assertEqual(response.status_code, 302)
#
#     def test_signup_if_keyerror_and_is_authenticated(self):
#         """
#         If keyerror and is_authenticated
#         """
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('sap:sign-up-done'))
#         self.assertEqual(response.status_code, 302)
