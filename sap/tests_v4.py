"""
contains unit tests for sap app
"""
import os
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
from django.urls import reverse
from sap.models import EventInviteeRelation, AllyStudentCategoryRelation, StudentCategories, Ally, Event
from .upload_resource_to_azure import upload_file_to_azure

User = get_user_model()


class AdminAnnoucementFeatureTests(TestCase):
    """
    Unit tests for features on the Admin dashboard
    """

    def setUp(self):
        self.username = 'admin_annoucement'
        self.password = 'admin_annoucement'
        self.email = 'email_annoucement@test.com'
        self.client = Client()

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

    def test_create_announcement_for_admin(self):
        """
        Test creation of annoucement for admin
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/create_announcements/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'title': 'Test Annoucement',
                'desc': 'Description of test announcement'
            }, follow=True
        )

        self.assertContains(
            response, "Annoucement created successfully !!", html=True
        )

        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()

        response = self.client.post(
            '/create_announcements/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'title': 'Test Annoucement',
                'desc': 'Description of test announcement'
            }, follow=True
        )

        self.assertEqual(response.status_code, 403)

    def test_annoucment_view_page(self):
        """
        Test viewing annoucements for admin
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/create_announcements/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'title': 'Test Annoucement',
                'desc': 'Description of test announcement'
            }, follow=True
        )

        self.assertContains(
            response, "Annoucement created successfully !!", html=True
        )

        response = self.client.get('/announcements/')
        self.assertEqual(response.status_code, 200)

        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()

        response = self.client.get('/announcements/')
        self.assertEqual(response.status_code, 200)


class TestUploadFileAzure(TestCase):
    """
    Test upload file to azure functionality
    """

    def test_upload_file(self):
        """
        Tests uploading resource to azure functionality
        @return:  True if succeeds
        """
        local_path = "/tmp"
        local_file_name = "quickstart" + ".txt"
        upload_file_path = os.path.join(local_path, local_file_name)

        # Write text to the file
        file = open(upload_file_path, 'w')
        file.write("Hello, World!")
        file.close()

        uploaded_resource_url_in_cloud = upload_file_to_azure(local_file_name, called_by_test_function=True)

        self.assertIn(
            "https://sepibafiles.blob.core.windows.net/sepibacontainer/", uploaded_resource_url_in_cloud
        )


class ResponseEventInvitationTests(TestCase):
    """
    Unit tests for calendar view
    """

    def setUp(self):
        self.admin_username = 'admin'
        self.admin_password = 'admin_password1'
        self.ally_username = 'ally'
        self.ally_password = 'ally_password1'
        self.client = Client()

        self.event = Event.objects.create(
            title='Internship',
            description='Internship',
            start_time='2021-04-20 21:05:00',
            end_time='2021-04-26 21:05:00',
            location='MacLean',
            num_invited=30,
            num_attending=10,
        )

        self.admin_user = User.objects.create_user(
            username=self.admin_username,
            email='email@test.com',
            password=self.admin_password,
            is_staff=True,
        )

        self.ally_user = User.objects.create_user(
            username=self.ally_username,
            email='allyemail@test.com',
            password=self.ally_password,
            is_staff=False,
        )

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='john',
            user_type='Graduate Student',
            works_at='College of Engineering',
            area_of_research='Biology',
            major='Biomedical Engineering',
            willing_to_volunteer_for_events=True,
        )

        self.category = StudentCategories.objects.create(lgbtq=True)
        self.student_ally_rel = AllyStudentCategoryRelation.objects.create(
            ally=self.ally,
            student_category=self.category,
        )

        self.event_ally_rel = EventInviteeRelation.objects.create(
            ally_id=self.ally.id,
            event_id=self.event.id,
        )

    def test_successfully_signup_event(self):
        """
        Successfully sign up for event if haven't done so
        """
        self.client.login(username=self.ally_username, password=self.ally_password)
        response = self.client.get('/signup_event/', {'event_id': self.event.id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "You have successfully signed up for this event!")

    def test_already_signup_event(self):
        """
        Already sign up for event, cannot sign up again
        """
        self.client.login(username=self.ally_username, password=self.ally_password)
        self.client.get('/signup_event/', {'event_id': self.event.id}, follow=True)
        response = self.client.get('/signup_event/', {'event_id': self.event.id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "You have already signed up for this event!")

    def test_not_invited_signup_event(self):
        """
        Cannot sign up if not invited
        """
        event = Event.objects.get(pk=self.event_ally_rel.event_id)
        event.delete()
        self.client.login(username=self.ally_username, password=self.ally_password)
        response = self.client.get('/signup_event/', {'event_id': self.event.id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'You cannot sign up for this event since you are not invited.')

    # def test_signup_event_ally_not_found(self):
    #     """
    #     Cannot sign up when there is no ally model
    #     """
    #     ally = Ally.objects.get(pk=self.ally.pk)
    #     ally.delete()
    #     self.client.login(username=self.ally_username, password=self.ally_password)
    #     response = self.client.get('/signup_event/', {'event_id': self.event.id}, follow=True)
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
    #     message = list(response.context['messages'])[0]
    #     self.assertEqual(message.message, 'Access denied. You are not registered in our system.')


class AllyEventInformation(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='eventAdmin', password='123456789', is_staff=True)
        self.user = User.objects.create_user(username='ally', password='123456789', is_staff=False)
        self.ally = Ally.objects.create(hawk_id=self.user.username, user=self.user, user_type='Undergraduate Student',
                                        major='biomedical Engineering', year='Freshman')
        self.client = Client()

    def test_get_event_info_page(self):
        self.client.login(username='eventAdmin', password='123456789')
        response = self.client.get(reverse('sap:view_ally_event_information', args=['ally']))
        self.assertEqual(response.status_code, 200)

    def test_redirect_bad_username(self):
        self.client.login(username='eventAdmin', password='123456789')
        response = self.client.get(reverse('sap:view_ally_event_information', args=['junkjunkjunk']))
        self.assertEqual(response.status_code, 302)


class EditEventTests(TestCase):
    """
    Tests for Edit Event feature
    """

    def setUp(self):
        """
        Setting up event and creating it for edit event
        """
        self.username = 'iba_test_admin'
        self.password = 'ibatestadminpass'
        self.email = 'ibaadmin@test.com'
        self.client = Client()

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.event = Event.objects.create(title='Mock Interview',
                                          description='Workshop for mock interviews',
                                          location='MacLean Hall',
                                          allday=True,
                                          end_time='2021-04-22 01:57:00',
                                          start_time='2021-04-22 00:57:00',
                                          num_attending=0,
                                          num_invited=5,
                                          mentor_status='Mentors,Mentees',
                                          research_field='Biochemistry,Bioinformatics',
                                          role_selected='Freshman,Sophomore,Juniors,Faculty',
                                          invite_all=True,
                                          special_category='First generation college-student,Rural,Low-income,Underrepresented racial/ethnic minority,Disabled,Transfer Student,LGBTQ'
                                          )

        self.event2 = Event.objects.create(title='Mock Interview2',
                                          description='Another Workshop for mock interviews',
                                          location='MacLean Hall',
                                          allday=False,
                                          end_time='2021-04-24 01:57:00',
                                          start_time='2021-04-22 00:57:00',
                                          num_attending=0,
                                          num_invited=5,
                                          mentor_status='Mentors,Mentees',
                                          research_field='Biochemistry,Bioinformatics',
                                          role_selected='Freshman,Sophomore,Juniors,Faculty',
                                          invite_all=False,
                                          special_category='First generation college-student,Underrepresented racial/ethnic minority,Disabled,Transfer Student'
                                          )

        self.ally_user = User.objects.create_user(username='john2',
                                                  email='john2@uiowa.edu',
                                                  password='johndoe2',
                                                  first_name='John2',
                                                  last_name='Doe',
                                                  is_active=True,
                                                  )

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe2',
            user_type='Graduate Student',
            works_at='College of Engineering',
            area_of_research='Biochemistry',
            major='Electrical Engineering',
            willing_to_volunteer_for_events=True
        )

        self.category = StudentCategories.objects.create(lgbtq=True,
                                                         rural=True,
                                                         first_gen_college_student=True,
                                                         transfer_student=True,
                                                         low_income=True,
                                                         disabled=True,
                                                         under_represented_racial_ethnic=True)
        self.student_ally_rel = AllyStudentCategoryRelation.objects.create(
            ally=self.ally,
            student_category=self.category,
        )

    def test_view_edit_event(self):
        """
        Admin can view the edit event page
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            '/edit_event/', {'event_id': self.event.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_event(self):
        """
        Testing whether admin can edit an event or not
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            '/edit_event/?event_id={0}'.format(self.event.id),
            {'csrfmiddlewaretoken': ['6soMcEK3d6JkcDRRnOu6XcdeVETyLibPQCZAuk1yHPHjjpSgxH2pUdQcOusmiiHG'],
             'start_time': ['2021-04-23T22:31'],
             'end_time': ['2021-04-25T18:31'],
             'allday': ['allday'],
             'event_location': ['MacLean Hall'],
             'invite_all': ['invite_all'],
             'role_selected': ['Staff', 'Graduate Student', 'Undergraduate Student', 'Faculty'],
             'school_year_selected': ['Freshman', 'Sophomore', 'Juniors', 'Faculty'],
             'mentor_status': ['Mentors', 'Mentees'],
             'special_category': ['First generation college-student', 'Rural', 'Low-income', 'Underrepresented racial/ethnic minority', 'Disabled', 'Transfer Student', 'LGBTQ'],
             'research_area': ['Biochemistry', 'Bioinformatics', 'Biology', 'Biomedical Engineering', 'Chemical Engineering', 'Chemistry', 'Computer Science and Engineering', 'Environmental Science', 'Health and Human Physiology', 'Mathematics', 'Microbiology', 'Neuroscience', 'Nursing', 'Physics', 'Psychology']
             }, follow=True
        )
        event = Event.objects.filter(title=self.event.title)
        assert event.exists()
        assert EventInviteeRelation.objects.filter(event=event[0], ally=self.ally).exists()
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_end_time_less_than_start_time(self):
        """
        Testing whether admin can edit an event or not
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            '/edit_event/?event_id={0}'.format(self.event.id),
            {'csrfmiddlewaretoken': ['6soMcEK3d6JkcDRRnOu6XcdeVETyLibPQCZAuk1yHPHjjpSgxH2pUdQcOusmiiHG'],
             'start_time': ['2021-04-23T22:31'],
             'end_time': ['2021-04-23T18:31'],
             'allday': ['allday'],
             'event_location': ['MacLean Hall'],
             'invite_all': ['invite_all'],
             'role_selected': ['Staff', 'Graduate Student', 'Undergraduate Student', 'Faculty'],
             'school_year_selected': ['Freshman', 'Sophomore', 'Juniors', 'Faculty'],
             'mentor_status': ['Mentors', 'Mentees'],
             'special_category': ['First generation college-student', 'Rural', 'Low-income', 'Underrepresented racial/ethnic minority', 'Disabled', 'Transfer Student', 'LGBTQ'],
             'research_area': ['Biochemistry', 'Bioinformatics', 'Biology', 'Biomedical Engineering', 'Chemical Engineering', 'Chemistry', 'Computer Science and Engineering', 'Environmental Science', 'Health and Human Physiology', 'Mathematics', 'Microbiology', 'Neuroscience', 'Nursing', 'Physics', 'Psychology']
             }
            , follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "End time cannot be less than start-time")

    def test_edit_not_all_invited_event(self):
        """
        Testing if an event with invite all and categories selected can be edited
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()

        self.client.login(username=self.username, password=self.password)

        response = self.client.post('/edit_event/?event_id={0}'.format(self.event2.id),
            {'csrfmiddlewaretoken': [
                '6soMcEK3d6JkcDRRnOu6XcdeVETyLibPQCZAuk1yHPHjjpSgxH2pUdQcOusmiiHG'],
             'start_time': ['2021-04-23T22:31'],
             'end_time': ['2021-04-25T18:31'],
             'allday': ['allday'],
             'event_location': ['MacLean Hall'],
             'role_selected': ['Staff', 'Graduate Student', 'Undergraduate Student', 'Faculty'],
             'school_year_selected': ['Freshman', 'Sophomore', 'Juniors', 'Faculty'],
             'mentor_status': ['Mentors', 'Mentees'],
             'special_category': ['First generation college-student', 'Rural', 'Low-income',
                                  'Underrepresented racial/ethnic minority', 'Disabled',
                                  'Transfer Student', 'LGBTQ'],
             'research_area': ['Biochemistry', 'Bioinformatics', 'Biology',
                               'Biomedical Engineering', 'Chemical Engineering', 'Chemistry',
                               'Computer Science and Engineering', 'Environmental Science',
                               'Health and Human Physiology', 'Mathematics', 'Microbiology',
                               'Neuroscience', 'Nursing', 'Physics', 'Psychology']
             }
        )

        url = response.url
        event = Event.objects.filter(title=self.event2.title)
        assert url == '/calendar'
        assert event.exists()
        assert EventInviteeRelation.objects.filter(event=event[0], ally=self.ally).exists()
