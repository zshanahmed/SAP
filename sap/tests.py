import os
from django.http import response

from django.shortcuts import render
# tests file
from django.test import TestCase, Client
import pandas as pd
import numpy as np
import io
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Ally, StudentCategories, AllyStudentCategoryRelation, Event, EventAllyRelation
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus
from .forms import UpdateAdminProfileForm, UserResetForgotPasswordForm
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm

from django.contrib.messages import get_messages


# Create your tests here.
from .tokens import password_reset_token


class DummyTests(TestCase):

    def test_true(self):
        self.assertIs(True, True)

    def test_false(self):
        self.assertIs(False, False)


def create_ally(username, hawk_id):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    user_1 = User.objects.create_user(username=username,
                                      email='jlennon@beatles.com',
                                      password='glass onion',
                                      first_name='John',
                                      last_name='Beatles')

    return Ally.objects.create(user=user_1, hawk_id=hawk_id, user_type='student', works_at='College of Engineering', year='first',
                               major='Computer Science')


class AdminAllyTableFeatureTests(TestCase):
    def setUp(self):
        self.username = 'Admin_1'
        self.password = 'admin_password1'
        self.email = 'email@test.com'
        self.client = Client()

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.ally_user = User.objects.create_user(username='johndoe',
                                        email='johndoe@uiowa.edu',
                                        password='johndoe',
                                        first_name='John',
                                        last_name='Doe')

        self.ally_user1 = User.objects.create_user(username='johndoe1',
                                                  email='johndoe1@uiowa.edu',
                                                  password='johndoe1',
                                                  first_name='John1',
                                                  last_name='Doe1')

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe',
            user_type='Staff',
            works_at='College of Engineering',
            area_of_research='Computer Science and Engineering,Health and Human Physiology,Physics',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=True,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

        self.ally1 = Ally.objects.create(
            user=self.ally_user1,
            hawk_id='johndoe1',
            user_type='Staff',
            works_at='College of Engineering',
            area_of_research='Computer Science and Engineering,Health and Human Physiology,Physics',
            description_of_research_done_at_lab='Created tools to fight fingerprinting',
            people_who_might_be_interested_in_iba=True,
            how_can_science_ally_serve_you='Help in connecting with like minded people',
            year='Senior',
            major='Electical Engineering',
            willing_to_offer_lab_shadowing=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentoring=True,
            interested_in_connecting_with_other_mentors=True,
            interested_in_mentor_training=True,
            interested_in_joining_lab=True,
            has_lab_experience=True,
            information_release=True,
            openings_in_lab_serving_at=True,
        )

    def test_edit_ally_page_for_admin(self):
        """
        Show and Complete Edit ally page for admin
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Testing for Staff user type
        response = self.client.get(
            '/edit_allies/', {'username': self.ally_user.username})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Edit Ally Profile", html=True
        )

        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': [self.ally_user.username],
                'studentsInterestedRadios': [str(self.ally.people_who_might_be_interested_in_iba)],
                'howCanWeHelp': ['Finding Jobs']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Ally updated !")

        # Testing for Graduate Student user type
        self.ally.user_type="Graduate Student"
        self.ally.save()
        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': [self.ally_user.username],
                'stemGradCheckboxes': ['Bioinformatics','Computer Science and Engineering', 'Health and Human Physiology', 'Neuroscience', 'Physics'],
                'mentoringGradRadios': ['Yes'],
                'labShadowRadios': ['No'],
                'connectingRadios': ['No'],
                'volunteerGradRadios': ['No'],
                'gradTrainingRadios': ['Yes']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Ally updated !")

        # Testing for UnderGrad Student user type
        self.ally.user_type = "Undergraduate Student"
        self.ally.save()
        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': [self.ally_user.username],
                'undergradRadios': ['Freshman'], 'major': ['Psychology'], 'interestRadios': ['No'], 'experienceRadios': ['Yes'], 'interestedRadios': ['No'], 'agreementRadios': ['Yes']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Ally updated !")

        # Testing for Faculty user type
        self.ally.user_type = "Faculty"
        self.ally.save()
        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': [self.ally_user.username],
                'stemGradCheckboxes': ['Biochemistry', 'Bioinformatics', 'Biology'], 'research-des': ['Authorship Obfuscation'], 'openingRadios': ['No'], 'mentoringFacultyRadios': ['No'], 'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Ally updated !")

    def test_edit_non_ally_page_for_admin(self):
        """
        Show that the code return 404 when username is wrong
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            '/edit_allies/', {'username': 'something'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': ['somthing'],
                'studentsInterestedRadios': [str(self.ally.people_who_might_be_interested_in_iba)],
                'howCanWeHelp': ['Finding Jobs']
            }, follow=True
        )
        self.assertContains(
            response, "Science Alliance Portal", html=True
        )
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Ally does not exist !")

    def test_view_ally_page_for_admin(self):
        """
        Show View ally page for admin
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/allies/', {'username': self.ally_user.username})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Ally Profile", html=True
        )

    def test_view_non_ally_page_for_admin(self):
        """
        Show that the code return 404 when username is wrong
        """

        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            '/allies/', {'username': 'something'})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_view_ally_page_for_non_admin(self):
        """
        Show that the code return 403 when user is not admin
        """

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(
            '/allies/', {'username': self.ally_user1.username})
        self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_delete_ally(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        name = self.ally_user.first_name + ' ' + self.ally_user.last_name

        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertContains(response, name, html=True)
        response = self.client.get('/delete/', {'username': self.ally_user.username}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, name, html=True)

    def test_delete_ally_fail(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        name = self.ally_user.first_name + " " + self.ally_user.last_name

        response = self.client.get(reverse("sap:sap-dashboard"))
        self.assertContains(response, name, html=True)
        response = self.client.get("/delete/", {"username": "nouserfound"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AdminUpdateProfileAndPasswordTests(TestCase):
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

class AlliesIndexViewTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        user = User.objects.create_user(self.username, 'email@test.com', self.password)
        user.is_staff = True
        user.save()

    def test_no_ally(self):
        """
        If no allies exist, an appropriate message is displayed.
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No allies are available.")
        self.assertQuerysetEqual(response.context['allies_list'], [])


    def test_one_ally(self):
        """
        Only one ally should be displayed on the home page
        """
        self.client.login(username=self.username, password=self.password)
        create_ally('username_1', 'hawk_id_1')
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertQuerysetEqual(
            response.context['allies_list'],
            ['<Ally: hawk_id_1>']
        )

    def test_two_allies(self):
        """
        Only two allies should be displayed on the home page
        """
        self.client.login(username=self.username, password=self.password)
        create_ally('username_1', 'hawk_id_1')
        create_ally('username_2', 'hawk_id_2')
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertQuerysetEqual(
            response.context['allies_list'],
            ['<Ally: hawk_id_2>', '<Ally: hawk_id_1>'] # Need to return in the descending order (When the ally record was created in the table)
        )

class CreateAdminViewTest(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.c = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.c.login(username=self.username, password=self.password)
        self.user.is_staff = True
        self.user.save()

    def test_get(self):
        """
        test get create admin page
        """
        response = self.c.get('/create_iba_admin/')
        self.assertEqual(response.status_code, 200)

    def test_post_missing_data(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['iba_admin'],
                'current_password': ['iba_sep_1'], 'new_email': [''],
                'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_Invalid_credentials(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_assword1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_new_username_that_exists(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['admin'], 'new_password': ['admin_password1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_non_matching_new_password(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['admin1'], 'new_password': ['admin_password1'],
                'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_good_create_admin(self):
        response = self.c.post('/create_iba_admin/', {'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                'current_username': ['admin'],
                'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
                'new_username': ['admin1'], 'new_password': ['admin_password1'],
                'repeat_password': ['admin_password1']})

        url = response.url
        assert url == '/dashboard'
        assert User.objects.filter(username='admin1').exists()

    '''
    TODO: Once we do performance enhancement - pagination, this test will be useful
    def test_51_allies(self):
        """
        Only 50 allies should be displayed on the home page even if there are more than 50 allies in the database
        """
        self.client.login(username=self.username, password=self.password)

        for i in range(52):
            create_ally('username_{}'.format(str(i)), 'hawk_id_{}'.format(str(i)))

        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertQuerysetEqual(
            len(response.context['allies_list'].count()),
            50
        )
        '''


class LoginRedirectTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        user1 = User.objects.create_user(username ='admin', email='email@test.com', password='admin_password1',
                                         is_staff=True)
        user1 = User.objects.create_user(username='nonadmin', email='email@test.com', password='admin_password2',
                                         is_staff=False)

    def test_login_for_admin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username='admin', password='admin_password1')
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()

    def test_login_for_admin_fail(self):
        """
        Invalid password error for admin
        """
        self.client.post("/", {"username": "adm", "password": "admin"})
        response = self.client.get(reverse("sap:home"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_for_nonadmin(self):
        """
        Non-admin users are redirected to About page
        """
        self.client.login(username='nonadmin', password='admin_password2')
        response = self.client.get(reverse('sap:sap-about'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()

class LogoutRedirectTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=True)

    def test_logout_for_admin(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:logout'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, '/')


class AdminAccessTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=True)

    def test_dashboard_access_for_admin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_analytics_access_for_admin(self):
        """
        Admin users can access Analytics
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class SignUpTests(TestCase):
    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.c = Client()

    def test_get(self):
        response = self.c.get('/sign-up/')
        self.assertEqual(response.status_code, 200)

    def test_entered_existing_user(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                                  'firstName': ['Elias'], 'lastName': ['Shaeffer'], 'new_username': ['admin'],
                                  'new_email': ['eshaeffer@uiowa.edu'], 'new_password': ['ddd'], 'repeat_password':
                                      ['dddd'], 'roleSelected': ['Graduate Student'],
                                  'stemGradCheckboxes': ['Biochemistry'], 'mentoringGradRadios': ['Yes'],
                                  'mentoringGradCheckboxes': ['First generation college-student'],
                                  'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'],
                                  'volunteerGradRadios': ['Yes'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_entered_existing_email(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                                  'firstName': ['Elias'], 'lastName': ['Shaeffer'], 'new_username': ['admin1'],
                                  'new_email': ['email@test.com'], 'new_password': ['ddd'], 'repeat_password':
                                      ['dddd'], 'roleSelected': ['Graduate Student'],
                                  'stemGradCheckboxes': ['Biochemistry'], 'mentoringGradRadios': ['Yes'],
                                  'mentoringGradCheckboxes': ['First generation college-student'],
                                  'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'],
                                  'volunteerGradRadios': ['Yes'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_password_not_same(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['MIyNUVJILbLGKrHXjz4m4fWt4d13TUOkkvRtCpStSmxkW8PKomuz3ESTYF8VVQil'],
                                  'firstName': ['Elias'], 'lastName': ['Shaeffer'], 'new_username': ['admin1123'],
                                  'new_email': ['email123@test.com'], 'new_password': ['ddd'], 'repeat_password':
                                      ['ddddd'], 'roleSelected': ['Graduate Student'],
                                  'stemGradCheckboxes': ['Biochemistry'], 'mentoringGradRadios': ['Yes'],
                                  'mentoringGradCheckboxes': ['First generation college-student'],
                                  'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'],
                                  'volunteerGradRadios': ['Yes'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/sign-up')
        self.assertEqual(response.status_code, 302)

    def test_create_Undergrad(self):
        response = self.c.post('/sign-up/', { 'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                                              'firstName': ['Zeeshan'], 'lastName': ['Ahmed'], 'new_username': ['zeeahmed'],
                                              'new_email': ['zeeahmed@uiowa.edu'], 'new_password': ['bigchungus'],
                                              'repeat_password': ['bigchungus'], 'roleSelected': ['Undergraduate Student'],
                                              'undergradRadios': ['Senior'], 'idUnderGradCheckboxes': ['First generation college-student'],
                                              'major': ['Computer Science'], 'interestRadios': ['Yes'],
                                              'experienceRadios': ['Yes'], 'interestedRadios': ['Yes'],
                                              'agreementRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_create_Undergrad(self):
        response = self.c.post('/sign-up/', { 'csrfmiddlewaretoken': ['At4HFZNsApVRWNye2Jcj4RVcWYf1fviv1kFbSZevLnNmJrWz4OyZhcAPn0JeaknZ'],
                                              'firstName': ['Zeeshan'], 'lastName': ['Ahmed'], 'new_username': ['zeeahmed1'],
                                              'new_email': ['zeeahmed@uiowa.edu'], 'new_password': ['bigchungusmyNameGunga'],
                                              'repeat_password': ['bigchungusmyNameGunga'], 'roleSelected': ['Undergraduate Student'],
                                              'undergradRadios': ['Senior'], 'major': ['Computer Science'], 'interestRadios': ['Yes'],
                                              'experienceRadios': ['Yes'], 'interestedRadios': ['Yes'],
                                              'agreementRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed1")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_create_Grad(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'],
        'firstName': ['glumpy'], 'lastName': ['guy'], 'new_username': ['big_guy1'],
        'new_email': ['eshaeffer@uiowa.edu'], 'new_password': ['123myNameGunga'], 'repeat_password': ['123myNameGunga'],
        'roleSelected': ['Graduate Student'],
        'stemGradCheckboxes': ['Biochemistry', 'Biology', 'Biomedical Engineering', 'Chemical Engineering'],
        'mentoringGradRadios': ['Yes'], 'mentoringGradCheckboxes': ['First generation college-student', 'Low-income', 'Underrepresented racial/ethnic minority', 'Transfer student', 'LGBTQ'],
        'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'], 'volunteerGradRadios': ['No'], 'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy1")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_create_Grad_noBoxes(self):
        response = self.c.post('/sign-up/', {
            'csrfmiddlewaretoken': ['TFosu1rFWp6S4SsYIV5Rb9FtBzoTavgrCsu31o9hTp975IuRpZeNgPJeBQiU6Cy5'],
            'firstName': ['glumpy'], 'lastName': ['guy'], 'new_username': ['big_guy12'],
            'new_email': ['eshaeffer@uiowa.edu'], 'new_password': ['123myNameGunga'], 'repeat_password': ['123myNameGunga'],
            'roleSelected': ['Graduate Student'],
            'mentoringGradRadios': ['Yes'],
            'labShadowRadios': ['Yes'], 'connectingRadios': ['Yes'], 'volunteerGradRadios': ['No'],
            'gradTrainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy12")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())


    def test_Faculty(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'], 'firstName': ['Terry'], 'lastName': ['Braun'],
        'new_username': ['tbraun'], 'new_email': ['tbraun@uiowa.edu'], 'new_password': ['123myNameGunga'],
        'repeat_password': ['123myNameGunga'], 'roleSelected': ['Faculty'],
        'stemCheckboxes': ['Bioinformatics', 'Biomedical Engineering'], 'research-des': ['Me make big variant :)'],
        'openingRadios': ['Yes'], 'mentoringCheckboxes': ['First generation college-student', 'Underrepresented racial/ethnic minority', 'Transfer student'],
        'volunteerRadios': ['Yes'],'mentoringFacultyRadios':['Yes'], 'trainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="tbraun")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_Faculty_noSelect(self):
        response = self.c.post('/sign-up/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'firstName': ['Terry'], 'lastName': ['Braun'],
            'new_username': ['tbraun2'], 'new_email': ['tbraun@uiowa.edu'], 'new_password': ['123myNameGunga'],
            'repeat_password': ['123myNameGunga'], 'roleSelected': ['Faculty'],
            'research-des': ['Me make big variant :)'],
            'openingRadios': ['Yes'],
            'volunteerRadios': ['Yes'], 'mentoringFacultyRadios': ['Yes'], 'trainingRadios': ['Yes']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="tbraun2")
        ally = Ally.objects.filter(user_id=user[0].id)
        categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(categoryRelation.exists())
        self.assertTrue(categories.exists())

    def test_Staff(self):
        response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['K5dFCUih0K6ZYklAemhvIWSpCebK86zdx4ric6ucIPLUQhAdtdT7hhp4r5etxoJY'],
        'firstName': ['hawk'], 'lastName': ['herky'], 'new_username': ['hawkherky'], 'new_email': ['hawkherky@uiowa.edu'],
        'new_password': ['hawkmyNameGunga'], 'repeat_password': ['hawkmyNameGunga'], 'roleSelected': ['Staff'],
        'studentsInterestedRadios': ['Yes'], 'howCanWeHelp': ['sasdasdasd']})
        url = response.url
        self.assertEqual(url, '/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="hawkherky")
        ally = Ally.objects.filter(user_id=user[0].id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())

    def test_password_less_than_minimum(self):
        response = self.c.post(
            "/sign-up/",
            {
                "csrfmiddlewaretoken": [
                    "K5dFCUih0K6ZYklAemhvIWSpCebK86zdx4ric6ucIPLUQhAdtdT7hhp4r5etxoJY"
                ],
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

    # def test_Staff(self):
    #     response = self.c.post('/sign-up/', {'csrfmiddlewaretoken': ['PoY77CUhmZ70AsUF3C1nISUsVErkhMjLyb4IEZCTjZafBiWyKGajNyYdVVlldTBp'],
    #     'firstName': ['chongu'], 'lastName': ['gumpy'], 'new_username': ['chonguG'],
    #     'new_email': ['chongu@uiowa.edu'], 'new_password': ['123'], 'repeat_password': ['123'],
    #     'roleSelected': ['Staff'], 'studentsInterestedRadios': ['Yes'], 'howCanWeHelp': ['give me $10000000']})
    #     url = response.url
    #     self.assertEqual(url, '/')
    #     self.assertEqual(response.status_code, 302)
    #     user = User.objects.filter(username="chonguG")
    #     ally = Ally.objects.filter(user_id=user[0].id)
    #     categoryRelation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
    #     categories = StudentCategories.objects.filter(id=categoryRelation[0].student_category_id)
    #     self.assertTrue(user.exists())
    #     self.assertTrue(ally.exists())
    #     self.assertTrue(categoryRelation.exists())
    #     self.assertTrue(categories.exists())


class NonAdminAccessTests(TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()

        User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=False)

    def test_dashboard_access_for_nonadmin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-dashboard'))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_analytics_access_for_nonadmin(self):
        """
        Admin users can access Dashboard
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sap-analytics'))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class ForgotPasswordTest(TestCase):
    def setUp(self):
        self.username = 'user1'
        self.password = 'user_password1'
        self.email = 'email1@test.com'
        self.client = Client()
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

    def test_get(self):
        """
        The view is valid
        """
        # self.user.save()
        # self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:password-forgot'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, "Send me instructions!", html=True
        )

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
        Enter invalid email address and receive a message
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
        Successfully create new password
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
        Fail to create new password
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

    # def test_confirmation_link_not_exist(self):
    #     """
    #     Cannot open invalid confirmation link
    #     """
    #     validate = URLValidator(verify_exists=True)
    #     user = User.objects.create_user(username='admin',
    #                                     email='email@test.com',
    #                                     password='admin_password1',
    #                                     is_staff=False)
    #
    #     token = password_reset_token.make_token(user)
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     link = reverse('sap:password-forgot-confirm', args=[uid, token])
    #     request = self.client.get(link)
    #
    #     # user.delete()
    #     self.assertEqual(request.status_code, 500)




userFields = ['last_login', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']
allyFields = ['user_type', 'area_of_research', 'openings_in_lab_serving_at', 'description_of_research_done_at_lab',
              'interested_in_mentoring', 'interested_in_mentor_training', 'willing_to_offer_lab_shadowing',
              'interested_in_connecting_with_other_mentors', 'willing_to_volunteer_for_events', 'works_at',
              'people_who_might_be_interested_in_iba', 'how_can_science_ally_serve_you', 'year', 'major',
              'information_release', 'interested_in_being_mentored', 'interested_in_joining_lab',
              'has_lab_experience']
categoryFields = ['under_represented_racial_ethnic', 'first_gen_college_student', 'transfer_student', 'lgbtq', 'low_income', 'rural']
class DownloadAlliesTest(TestCase):


    def fields_helper(self, model, columns):
        for field in model._meta.get_fields():
            fields = str(field).split(".")[-1]
            if fields in userFields or fields in allyFields or fields in categoryFields:
                columns.append(fields)

        return columns

    def cleanup(self, dict):
        ar = []
        for item in dict.items():
            if item[0] in userFields or item[0] in allyFields or item[0] in categoryFields:
                if item[0] == 'date_joined':
                    ar.append(item[1].strftime("%b-%d-%Y"))
                else:
                    ar.append(item[1])
        return ar

    def setUp(self):
        User.objects.all().delete()
        Ally.objects.all().delete()
        StudentCategories.objects.all().delete()
        AllyStudentCategoryRelation.objects.all().delete()

        self.client = Client()

        self.loginuser = User.objects.create_user(username='glib', password='macaque', email='staff@uiowa.edu',
                                              first_name='charlie', last_name='hebdo', is_staff=True)

        self.user1 = User.objects.create_user(username='staff', password='123', email='staff@uiowa.edu',
                                              first_name='charlie', last_name='hebdo')
        self.user2 = User.objects.create_user(username='grad', password='123', email='gradf@uiowa.edu',
                                              first_name='wolfgang', last_name='kremple')
        self.user3 = User.objects.create_user(username='faculty', password='123', email='faculty@uiowa.edu',
                                              first_name='Elias', last_name='Shaeffer')
        self.user4 = User.objects.create_user(username='undergrad', password='123', email='undergrad@uiowa.edu',
                                              first_name='Zeeshan', last_name='Ahmed')

        self.ally1 = Ally.objects.create(user=self.user1, user_type='Staff', hawk_id=self.user1.username,
                                            people_who_might_be_interested_in_iba=True,
                                            how_can_science_ally_serve_you='help_me 0:')
        self.ally2 = Ally.objects.create(user=self.user2, user_type='Graduate Student', hawk_id=self.user2.username,
                                         area_of_research='Bioinformatics',
                                         interested_in_mentoring=False,
                                         willing_to_offer_lab_shadowing=True,
                                         interested_in_connecting_with_other_mentors=False,
                                         willing_to_volunteer_for_events=True,
                                         interested_in_mentor_training=False
                                         )
        self.ally3 = Ally.objects.create(user=self.user3, user_type='Faculty', hawk_id=self.user3.username,
                                         area_of_research='Biology',
                                         openings_in_lab_serving_at=True,
                                         description_of_research_done_at_lab='Big biology my guy',
                                         interested_in_mentoring=True,
                                         willing_to_volunteer_for_events=True,
                                         interested_in_mentor_training=True
                                         )
        self.ally4 = Ally.objects.create(user=self.user4, user_type='Undergraduate Student', hawk_id=self.user4.username,
                                         major='biomedical engineering', year='Freshman',
                                         interested_in_joining_lab=True, has_lab_experience=False,
                                         interested_in_mentoring=False,
                                         information_release=True
                                         )

        self.categories2 = StudentCategories.objects.create(rural=True, first_gen_college_student=True,
                                                            under_represented_racial_ethnic=True, transfer_student=True,
                                                            lgbtq=True, low_income=True)
        self.categories3 = StudentCategories.objects.create(rural=True, first_gen_college_student=False,
                                                            under_represented_racial_ethnic=True, transfer_student=True,
                                                            lgbtq=True, low_income=False)
        self.categories4 = StudentCategories.objects.create(rural=True, first_gen_college_student=False,
                                                            under_represented_racial_ethnic=True, transfer_student=False,
                                                            lgbtq=True, low_income=False)

        AllyStudentCategoryRelation.objects.create(ally_id=self.ally2.id, student_category_id=self.categories2.id)
        AllyStudentCategoryRelation.objects.create(ally_id=self.ally3.id, student_category_id=self.categories3.id)
        AllyStudentCategoryRelation.objects.create(ally_id=self.ally4.id, student_category_id=self.categories4.id)

        columns = []
        columns = self.fields_helper(User, columns)
        columns = self.fields_helper(Ally, columns)
        columns = self.fields_helper(StudentCategories, columns)

        data = []
        user1 = self.cleanup(self.user1.__dict__) + \
                self.cleanup(self.ally1.__dict__) + [None, None, None, None, None, None]
        user2 = self.cleanup(self.user2.__dict__) + \
                self.cleanup(self.ally2.__dict__) + self.cleanup(self.categories2.__dict__)

        user3 = self.cleanup(self.user3.__dict__) + \
                self.cleanup(self.ally3.__dict__) + self.cleanup(self.categories3.__dict__)
        user4 = self.cleanup(self.user4.__dict__) + \
                self.cleanup(self.ally4.__dict__) + self.cleanup(self.categories4.__dict__)

        data.append(user1)
        data.append(user2)
        data.append(user3)
        data.append(user4)

        df = pd.DataFrame(data=data, columns=columns)
        df = df.replace(0, False)
        df = df.replace(1, True)
        df.fillna(value=np.nan, inplace=True)
        df = df.replace('', np.nan)
        self.df = df

    def test_download_data(self):
        """
        Testing the download data feature. If I create 4 allies in the database - one of each type, complete with
        ally categories then they should each appear in the CSV
        """
        self.client.login(username='glib', password='macaque')
        response = self.client.get(reverse('sap:download_allies'))
        f = io.BytesIO(response.content)
        df = pd.read_csv(f)
        pd.testing.assert_frame_equal(df, self.df)

    def test_try_download_as_ally(self):
        """
        Testing the download data feature. I should get a 403 response if I try to get the path as regular user
        """
        self.client.login(username='staff', password='123')
        response = self.client.get(reverse('sap:download_allies'))
        self.assertEqual(response.status_code, 403)

class CreateEventTests(TestCase):
    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        self.ally_user = User.objects.create_user(username='johndoe',
                                                  email='johndoe@uiowa.edu',
                                                  password='johndoe',
                                                  first_name='John',
                                                  last_name='Doe')

        self.ally = Ally.objects.create(
            user=self.ally_user,
            hawk_id='johndoe',
            user_type='Graduate Student',
            works_at='College of Engineering',
            area_of_research='Biochemistry',
            major='Electrical Engineering',
            willing_to_volunteer_for_events=True
        )

        self.category = StudentCategories.objects.create(lgbtq=True)
        self.student_ally_rel = AllyStudentCategoryRelation.objects.create(
            ally=self.ally,
            student_category=self.category
        )

    def test_get(self):
        response = self.client.get('/create_event/')
        self.assertEqual(response.status_code, 200)

    def test_invite_all(self):
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event'],
            'event_description': ['description of the event'],
            'event_location': ['https://zoom.us/abc123edf'],
            'event_date_time': ['2021-03-31T15:32'],
            'invite_all': 'true'
        })

        url = response.url
        event = Event.objects.filter(title='title of the event')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_invite_biochem_student(self):
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event 2'],
            'event_description': ['description of the event 2'],
            'event_location': ['https://zoom.us/abc123edf2'],
            'event_date_time': ['2021-03-31T15:32'],
            'role_selected': ['Graduate Student'],
            'mentor_status': ['Mentors', 'Mentees'],
            'research_area': ['Biochemistry']
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 2')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()

    def test_invite_special_category_student(self):
        response = self.client.post('/create_event/', {
            'csrfmiddlewaretoken': ['gr9bKWMJLFrJZfcdKkdRhlyKLI0JeTh2ZefMhjulIFuY05e6romNm1CvLZUKa0zG'],
            'event_title': ['title of the event 3'],
            'event_description': ['description of the event 3'],
            'event_location': ['https://zoom.us/abc123edf2'],
            'event_date_time': ['2021-03-31T15:32'],
            'special_category': ['First generation college-student', 'Rural', 'Low-income', 'Underrepresented racial/ethnic minority', 'Transfer Student', 'LGBTQ'],
        })

        url = response.url
        event = Event.objects.filter(title='title of the event 3')
        assert url == '/dashboard'
        assert event.exists()
        assert EventAllyRelation.objects.filter(event=event[0], ally=self.ally).exists()