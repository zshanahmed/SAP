"""
contains unit tests for sap app
"""
import os
from http import HTTPStatus

from notifications.signals import notify
from notifications.models import Notification
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client  # tests file
from django.urls import reverse
from sap.models import EventInviteeRelation, AllyStudentCategoryRelation, StudentCategories, Ally, Event
from sap.views_v2 import urlsafe_base64_encode, force_bytes
from .upload_resource_to_azure import upload_file_to_azure
from .forms import UpdateAdminProfileForm, UserResetForgotPasswordForm
from .tokens import password_reset_token
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
            allday=0,
            invite_all=0,
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

    def test_successfully_deregister_event(self):
        """
        Successfully sign up for event if haven't done so
        """
        self.client.login(username=self.ally_username, password=self.ally_password)
        self.client.get('/signup_event/', {'event_id': self.event.id}, follow=True)
        response = self.client.get('/deregister_event/', {'event_id': self.event.id}, follow=True)


        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "You will no longer attend this event.")

    def test_cannot_deregister_event(self):
        """
        Already sign up for event, cannot sign up again
        """
        self.client.login(username=self.ally_username, password=self.ally_password)
        response = self.client.get('/deregister_event/', {'event_id': self.event.id}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "You did not sign up for this event.")

class AllyEventInformation(TestCase):
    """
    Tests View Ally Event Information in views_v3
    """
    def setUp(self):
        self.admin = User.objects.create_user(username='eventAdmin', password='123456789', is_staff=True)
        self.user = User.objects.create_user(username='ally', password='123456789', is_staff=False)
        self.ally = Ally.objects.create(hawk_id=self.user.username, user=self.user, user_type='Undergraduate Student',
                                        major='biomedical Engineering', year='Freshman')
        self.client = Client()

    def test_get_event_info_page(self):
        """
        checks if page gets the event info page given good username
        """
        self.client.login(username='eventAdmin', password='123456789')
        response = self.client.get(reverse('sap:view_ally_event_information', args=['ally']))
        self.assertEqual(response.status_code, 200)

    def test_redirect_bad_username(self):
        """
        checks if redirects given bad username
        """
        self.client.login(username='eventAdmin', password='123456789')
        response = self.client.get(reverse('sap:view_ally_event_information', args=['junkjunkjunk']))
        self.assertEqual(response.status_code, 302)


class AdminUpdateProfileAndPasswordTests(TestCase):
    """
    Unit test for update profile feature for admin and to reset their passwords
    """

    def setUp(self):
        self.username = 'Admin_1'
        self.password = 'admin_password1'
        self.email = 'email@test.com'
        self.client = Client()
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

    def test_change_password_page_for_admin(self):
        """
        Show Change Password page for Admin
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )

    def test_change_password_page_for_ally(self):
        """
        Show Change Password page for Ally
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_profile_page_for_admin(self):
        """
        Show Change Password page for Admin
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Update Admin Profile", html=True
        )

    def test_update_profile_page_for_ally(self):
        """
        Show Change Password page for Ally
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_failure_mismatched_new_pass_change_password(self):
        """
        If new passwords don't match, a failed message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )
        data = {
            "old_password": "admin_password1",
            "new_password1": "something_random",
            "new_password2": "admin_password2"
        }
        form = PasswordChangeForm(
            user=self.user,
            data=data
        )
        self.assertFalse(form.is_valid())

        response = self.client.post(
            reverse('sap:change_password'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Could not Update Password !")

    def test_failure_old_pass_wrong_change_password(self):
        """
        If old password is wrong, a failed message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )
        data = {
            "old_password": "something_random",
            "new_password1": "admin_password2",
            "new_password2": "admin_password2"
        }
        form = PasswordChangeForm(
            user=self.user,
            data=data
        )
        self.assertFalse(form.is_valid())
        response = self.client.post(
            reverse('sap:change_password'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Could not Update Password !")

    def test_success_change_password(self):
        """
        If old password is right and new password match then change password
        is successfull and a success message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Change Password", html=True
        )
        data = {
            "old_password": "admin_password1",
            "new_password1": "admin_password2",
            "new_password2": "admin_password2"
        }
        form = PasswordChangeForm(
            user=self.user,
            data=data
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse('sap:change_password'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Password Updated Successfully !")

    def test_correct_update_profile(self):
        """
        If profile is updated, a success message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Update Admin Profile", html=True
        )

        form = UpdateAdminProfileForm(
            data={"username": "Admin_2", "email": "admin@admin.com"})
        self.assertTrue(form.is_valid())
        response = self.client.post(
            reverse('sap:sap-admin_profile'), data={"username": "Admin_2", "email": "admin@admin.com"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Profile Updated !")

    def test_fail_update_profile(self):
        """
        If profile is not updated, a failed message is displayed
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-admin_profile'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Update Admin Profile", html=True
        )

        form = UpdateAdminProfileForm(
            data={"username": "Admin_1", "email": "admin@admin.com"})
        self.assertFalse(form.is_valid())
        response = self.client.post(
            "/update_profile/", data={"username": "Admin_1", "email": "admin@admin.com"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(
            message.message, "Could not Update Profile ! Username already exists")
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
                                          special_category='First generation college-student,'
                                                           'Rural,Low-income,'
                                                           'Underrepresented racial/ethnic minority,'
                                                           'Disabled,Transfer Student,LGBTQ'
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
                                          research_field='Biochemistry,'
                                                         'Bioinformatics',
                                          role_selected='Freshman,Sophomore,Juniors,Faculty',
                                          invite_all=False,
                                          special_category='First generation college-student,'
                                                           'Underrepresented racial/ethnic minority,'
                                                           'Disabled,Transfer Student'
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
            hawk_id='johndoe21',
            user_type='Graduate Student',
            works_at='College of Engineering',
            area_of_research='Computer Science and Engineering',
            major='Computer Science',
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
             'role_selected': ['Staff', 'Graduate Student',
                               'Undergraduate Student', 'Faculty'],
             'school_year_selected': ['Freshman',
                                      'Sophomore',
                                      'Juniors',
                                      'Faculty'],
             'mentor_status': ['Mentors', 'Mentees'],
             'special_category': ['First generation college-student', 'Rural',
                                  'Low-income', 'Underrepresented racial/ethnic minority',
                                  'Disabled', 'Transfer Student',
                                  'LGBTQ'],
             'research_area': ['Biochemistry', 'Bioinformatics',
                               'Biology', 'Biomedical Engineering',
                               'Chemical Engineering', 'Chemistry',
                               'Computer Science and Engineering',
                               'Environmental Science',
                               'Health and Human Physiology', 'Mathematics', 'Microbiology',
                               'Neuroscience', 'Nursing', 'Physics', 'Psychology']
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
             'special_category': ['First generation college-student', 'Rural',
                                  'Low-income', 'Underrepresented racial/ethnic minority',
                                  'Disabled', 'Transfer Student', 'LGBTQ'],
             'research_area': ['Biochemistry', 'Bioinformatics', 'Biology',
                               'Biomedical Engineering', 'Chemical Engineering',
                               'Chemistry', 'Computer Science and Engineering', 'Environmental Science',
                               'Health and Human Physiology', 'Mathematics', 'Microbiology',
                               'Neuroscience', 'Nursing', 'Physics', 'Psychology']
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

class SapNotifications(TestCase):
    """
    Test sap notification view
    """
    def setUp(self):
        recipient = User.objects.create_user(username='recipient', password='12345678')
        sender = User.objects.create_user(username='sender', password='12345678')
        self.notification = notify.send(sender, recipient=recipient, verb='testing testing 123')[0][1][0]
        self.other_notification = notify.send(recipient, recipient=sender, verb='not yo message')[0][1][0]
        self.client = Client()

    def test_get_page(self):
        """
        Test that a valid url exists for the notificaion page and it can be reached
        """
        self.client.login(username='recipient', password='12345678')
        response = self.client.get('/notification_center/')
        self.assertEqual(response.status_code, 200)

    def test_dismiss_not_yours(self):
        """
        Check that you cannot dismiss others' notifications
        """
        self.client.login(username='recipient', password='12345678')
        response = self.client.get(reverse('sap:dismiss_notification', args=[self.other_notification.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'Access Denied!')
        try:
            Notification.objects.get(id=self.other_notification.id)
        except ObjectDoesNotExist:
            assert False

    def test_dismiss_not_existing(self):
        """
        Test that you cannot dismiss non-existant notificaitons
        """
        self.client.login(username='recipient', password='12345678')
        response = self.client.get(reverse('sap:dismiss_notification', args=[0]), follow=True)
        self.assertEqual(response.status_code, 200)
        print(response.context['messages'])
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'Notification does not exist!')

    def test_dismiss(self):
        """
        Test the dismiss function on the notification page
        """
        self.client.login(username='recipient', password='12345678')
        response = self.client.get(reverse('sap:dismiss_notification', args=[self.notification.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'Notification Dismissed!')
        try:
            Notification.objects.get(id=self.notification.id)
            assert False
        except ObjectDoesNotExist:
            pass

class ForgotPasswordTest(TestCase):
    """
    Unit tests for forgot password feature
    """

    def setUp(self):
        self.username = 'user1'
        self.password = 'user_password1'
        self.email = 'email1@test.com'
        self.client = Client()
        self.user = User.objects.create_user(self.username, self.email, self.password)

    def test_get_success(self):
        """
        Can access if user is not logged in.
        """
        self.client.logout()
        response = self.client.get(reverse('sap:password-forgot'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Send me instructions!", html=True
        )

    def test_get_fail(self):
        """
        Cannot access if user is not logged in.
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:password-forgot'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_enter_valid_reset_email_address(self):
        """
        Enter email address and receive a message
        """
        response = self.client.get(reverse('sap:password-forgot'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Send me instructions!", html=True
        )

        data = {
            "email": "email1@test.com",
        }
        form = PasswordResetForm(
            data=data
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse("sap:password-forgot"), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_enter_invalid_reset_email_address(self):
        """
        Enter invalid email address and receive a message.
        """
        response = self.client.get(reverse('sap:password-forgot'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Send me instructions!", html=True
        )

        data = {
            "email": "wrongemail@test.com",
        }
        form = PasswordResetForm(
            data=data
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            reverse('sap:password-forgot'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_enter_invalid_form(self):
        """
        Enter invalid text in email field.
        """
        response = self.client.get(reverse('sap:password-forgot'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Send me instructions!", html=True
        )

        data = {
            "email": "not_an_email_address",
        }
        form = PasswordResetForm(
            data=data
        )
        self.assertFalse(form.is_valid())

        response = self.client.post(
            reverse('sap:password-forgot'), data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_if_confirmation_link_work(self):
        """
        The unique link to reset password exists and works
        """
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.OK)

    def test_reset_password_success(self):
        """
        Successfully create new password.
        """
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.OK)

        data = {
            "new_password1": "user_password2",
            "new_password2": "user_password2"
        }
        form = UserResetForgotPasswordForm(
            user=self.user,
            data=data
        )
        self.assertTrue(form.is_valid())

        response = self.client.post(
            link, data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "New Password Created Successfully!")

    def test_reset_password_failure(self):
        """
        Fail to create new password.
        """
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.OK)

        data = {
            "new_password1": "user_password2",
            "new_password2": "wrong_password"
        }
        form = UserResetForgotPasswordForm(
            user=self.user,
            data=data
        )
        self.assertFalse(form.is_valid())

        response = self.client.post(
            link, data=data, follow=True)
        # self.assertEqual(response.url, link)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_confirmation_link_fail_for_get_method(self):
        """
        Cannot open invalid confirmation link.
        """
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        self.user.delete()

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.FOUND)

    def test_confirmation_link_fail_for_post_method(self):
        """
        Fail to create new password.
        """
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.OK)

        data = {
            "new_password1": "user_password2",
            "new_password2": "user_password2"
        }
        form = UserResetForgotPasswordForm(
            user=self.user,
            data=data
        )
        self.assertTrue(form.is_valid())

        self.user.delete()

        response = self.client.post(
            link, data=data, follow=True)
        # self.assertEqual(response.url, link)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class ForgotPasswordDoneView(TestCase):
    """
    Unit tests for SignUpDoneView
    """

    def setUp(self):
        self.username = 'admin'
        self.username_active = 'user_active'
        self.password = 'admin_password1'
        self.email = 'email@test.com'
        self.email_active = 'email_active@test.com'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.user_active = User.objects.create_user(username=self.username_active, email=self.email_active,
                                                    password=self.password,
                                                    is_active=True)
        self.client = Client()

    def test_forgotpassword_if_keyerror(self):
        """
        If keyerror
        """
        self.client.logout()
        response = self.client.get(reverse('sap:password-forgot-done'))
        self.assertEqual(response.status_code, 302)

    def test_forgotpassword_if_keyerror_and_is_authenticated(self):
        """
        If keyerror and is_authenticated
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:password-forgot-done'))
        self.assertEqual(response.status_code, 302)
