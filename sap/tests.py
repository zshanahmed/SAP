"""
contains unit tests for sap app
"""
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UpdateAdminProfileForm
from .models import Ally

User = get_user_model()


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
    """
    Unit tests for features on the Admin dashboard
    """

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

        self.ally_user_2 = User.objects.create_user(username='johndoe_2',
                                                    email='johndoe@uiowa.edu',
                                                    password='johndoe',
                                                    first_name='John',
                                                    last_name='Doe',
                                                    is_active=False)

        self.ally_2 = Ally.objects.create(
            user=self.ally_user_2,
            hawk_id='johndoe_2',
            user_type='Staff',
            works_at='College of Engineering',
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

    def test_year_filter_for_admin(self):
        """
        Show all allies conforming to year filters
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Junior'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Senior'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_stem_aor_filter_for_admin(self):
        """
        Show all allies conforming to stem aor filters
        """
        self.user.is_staff = True
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Bioinformatics'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Physics'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
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
        self.ally.user_type = "Graduate Student"
        self.ally.save()
        response = self.client.post(
            '/edit_allies/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'username': [self.ally_user.username],
                'stemGradCheckboxes': ['Bioinformatics', 'Computer Science and Engineering', 'Health and Human Physiology',
                                       'Neuroscience', 'Physics'],
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
                'undergradRadios': ['Freshman'], 'major': ['Psychology'], 'interestRadios': ['No'], 'experienceRadios': ['Yes'],
                'interestedRadios': ['No'], 'agreementRadios': ['Yes']
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
                'stemGradCheckboxes': ['Biochemistry', 'Bioinformatics', 'Biology'], 'research-des': ['Authorship Obfuscation'],
                'openingRadios': ['No'], 'mentoringFacultyRadios': ['No'], 'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes']
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

    def test_delete_ally(self):
        """
        Unit test for delete ally feature
        """
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
        """
        Unit test for deleting non existent ally
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        name = self.ally_user.first_name + " " + self.ally_user.last_name

        response = self.client.get(reverse("sap:sap-dashboard"))
        self.assertContains(response, name, html=True)
        response = self.client.get("/delete/", {"username": "nouserfound"}, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AllyDashboardTests(TestCase):
    """
    Unit tests for features on the ally dashboard
    """

    def setUp(self):
        self.username = 'Ally_1'
        self.password = 'ally_password1'
        self.email = 'email_ally@test.com'
        self.client = Client()

        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.ally_user = User.objects.create_user(username='johndoe1',
                                                  email='johndoe1@uiowa.edu',
                                                  password='johndoe1',
                                                  first_name='John1',
                                                  last_name='Doe1')

        self.ally_user1 = User.objects.create_user(username='johndoe2',
                                                   email='johndoe2@uiowa.edu',
                                                   password='johndoe2',
                                                   first_name='John2',
                                                   last_name='Doe2')

        self.ally = Ally.objects.create(
            user=self.ally_user,
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

        self.ally_user_2 = User.objects.create_user(username='johndoe_3',
                                                    email='johndoe3@uiowa.edu',
                                                    password='johndoe3',
                                                    first_name='John3',
                                                    last_name='Doe3',
                                                    is_active=False)

        self.ally_2 = Ally.objects.create(
            user=self.ally_user_2,
            hawk_id='johndoe_3',
            user_type='Staff',
            works_at='College of Engineering',
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

    def test_dasbhoard_access_for_nonadmin(self):
        """
        Display non admin dashboard page for allies
        """
        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("sap:ally-dashboard"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_year_filter_for_nonadmin(self):
        """
        Show all allies conforming to year filters
        """
        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Junior'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'undergradYear': ['Senior'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )

    def test_stem_aor_filter_for_nonadmin(self):
        """
        Show all allies conforming to stem aor filters
        """
        self.user.is_staff = False
        self.user.is_active = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        # Should return no allies
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Bioinformatics'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, "No allies are available.", html=True
        )

        # Should find our johndoe
        response = self.client.post(
            '/ally-dashboard/', {
                'csrfmiddlewaretoken': ['XdNiZpT3jpCeRzd2kq8bbRPUmc0tKFP7dsxNaQNTUhblQPK7lne9sX0mrE5khfHH'],
                'stemGradCheckboxes': ['Physics'],
                'form_type': 'filters'
            }, follow=True
        )

        self.assertContains(
            response, self.ally_user.first_name + ' ' + self.ally_user.last_name, html=True
        )


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


class AlliesIndexViewTests(TestCase):
    """
    Unit tests for the dashboard an admin views
    """

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
            ['<Ally: hawk_id_2>', '<Ally: hawk_id_1>']  # Need to return in the descending order
        )


class CreateAdminViewTest(TestCase):
    """
    Unit tests for creating new IBA admins
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password)
        self.client.login(username=self.username, password=self.password)
        self.user.is_staff = True
        self.user.save()

    def test_get(self):
        """
        test get create admin page
        """
        response = self.client.get('/create_iba_admin/')
        self.assertEqual(response.status_code, 200)

    def test_post_missing_data(self):
        """
        Check if email entered for new admin is non empty
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['iba_admin'],
            'current_password': ['iba_sep_1'], 'new_email': [''],
            'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_invalid_credentials(self):
        """
        check if the current iba admin username and password are valid
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_assword1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['iba_admin'], 'new_password': ['iba_sep_1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_new_username_that_exists(self):
        """
        check if the new admin's name is unique
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['admin'], 'new_password': ['admin_password1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_post_non_matching_new_password(self):
        """
        verify if the password and confirm password fields have the same value
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
            'current_username': ['admin'],
            'current_password': ['admin_password1'], 'new_email': ['emailGuy@email.com'],
            'new_username': ['admin1'], 'new_password': ['admin_password1'],
            'repeat_password': ['iba_sep_1']})

        url = response.url
        assert url == '/create_iba_admin'

    def test_good_create_admin(self):
        """
        Test if new admin is created in user table if all fields are valid
        """
        response = self.client.post('/create_iba_admin/', {
            'csrfmiddlewaretoken': ['AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
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
    """
    Unit tests to verify if the users are redirected to proper page after login
    """

    def setUp(self):
        self.username = 'user'
        self.password = 'user_password1'
        self.email = 'email@test.com'
        self.client = Client()

        self.user = User.objects.create_user(self.username, self.email, self.password)

    def test_login_for_admin(self):
        """
        Admin users are redirected to Dashboard after logging in
        """
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("sap:login_success"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

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
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse("sap:login_success"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class LogoutRedirectTests(TestCase):
    """
    Unit tests to verify if logout happens properly
    """

    def setUp(self):
        self.username = 'admin'
        self.password = 'admin_password1'
        self.client = Client()
        self.user = User.objects.create_user(self.username, 'email@test.com', self.password, is_staff=True)

    def test_logout_for_admin(self):
        """
        test if admin is logged out on click of logout button
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:logout'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, '/')

    def test_logout_for_ally(self):
        """
        test if admin is logged out on click of logout button
        """
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:logout'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, '/')


class AdminAccessTests(TestCase):
    """
    Tests to ensure admin is able to access all the pages on the site
    """

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
