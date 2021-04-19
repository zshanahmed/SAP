"""
contains unit tests for sap app
"""

from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.forms import PasswordResetForm
from .forms import UserResetForgotPasswordForm
from .models import Ally, StudentCategories, AllyStudentCategoryRelation

# Create your tests here.
from .tokens import password_reset_token, account_activation_token

User = get_user_model()

class SignUpTests(TestCase):
    """
    Testing all different scenarios of signup for different types of users
    """

    def setUp(self):
        self.username = 'admin'
        self.username_active = 'user_active'
        self.password = 'admin_password1'
        self.email = 'email@test.com'
        self.email_active = 'email_active@test.com'
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
        self.assertEqual(url, '/sign-up-done/')
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
                'new_username': ['admin1'],
                'new_email': self.user_active.email,
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
        Test signup feature using undergrad user
        """
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
        self.assertEqual(url, '/sign-up-done/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="zeeahmed1")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(categories.exists())

    def test_create_grad(self):
        """
        Test signup feature using a grad user
        """

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
                'areaOfResearchCheckboxes': ['Bioinformatics'], 'research-des': ['research'],
                'openingRadios': ['No'], 'mentoringRadios': ['No'], 'connectingWithMentorsRadios': ['Yes'],
                'studentsInterestedRadios': ['No'], 'mentorCheckboxes': ['Low-income'], 'labShadowRadios': ['Yes'],
                'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes'], 'howCanWeHelp': ['no']
            }
        )
        url = response.url
        self.assertEqual(url, '/sign-up-done/')
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(username="big_guy1")
        ally = Ally.objects.filter(user_id=user[0].id)
        category_relation = AllyStudentCategoryRelation.objects.filter(ally_id=ally[0].id)
        categories = StudentCategories.objects.filter(id=category_relation[0].student_category_id)
        self.assertTrue(user.exists())
        self.assertTrue(ally.exists())
        self.assertTrue(category_relation.exists())
        self.assertTrue(categories.exists())

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
        self.assertEqual(url, '/sign-up-done/')
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


class SignUpDoneViewTests(TestCase):
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

    def test_if_user_come_from_signup(self):
        """
        If user comes from sign-up, redirect to the page
        """
        response = self.client.post(
            '/sign-up/',
            {
                'csrfmiddlewaretoken': ['K5dFCUih0K6ZYklAemhvIWSpCebK86zdx4ric6ucIPLUQhAdtdT7hhp4r5etxoJY'],
                'firstName': ['hawk'],
                'lastName': ['herky'],
                'new_username': ['hawkherky'],
                'new_email': ['hawkherky@uiowa.edu'],
                'new_password': self.password,
                'repeat_password': self.password,
                'roleSelected': ['Graduate Student'],
                'research-des': ['research'],
                'openingRadios': ['No'], 'mentoringRadios': ['No'], 'connectingWithMentorsRadios': ['Yes'],
                'studentsInterestedRadios': ['No'], 'labShadowRadios': ['Yes'],
                'volunteerRadios': ['Yes'], 'trainingRadios': ['Yes'], 'howCanWeHelp': ['no']
            }
        )

        # response2 = response
        url = response.url
        self.assertEqual(url, '/sign-up-done/')
        self.assertEqual(response.status_code, 302)

    def test_signup_if_user_is_authenticated(self):
        """
        If user is authenticated
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sign-up-done'))
        self.assertEqual(response.status_code, 302)

    def test_signup_if_keyerror(self):
        """
        If keyerror
        """
        self.client.logout()
        response = self.client.get(reverse('sap:sign-up-done'))
        self.assertEqual(response.status_code, 302)

    def test_signup_if_keyerror_and_is_authenticated(self):
        """
        If keyerror and is_authenticated
        """
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sap:sign-up-done'))
        self.assertEqual(response.status_code, 302)


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
