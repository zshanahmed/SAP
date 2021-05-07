"""
contains unit tests for sap app
"""
from http import HTTPStatus

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
from django.urls import reverse
from sap.models import Ally
from sap.views_v2 import urlsafe_base64_encode, force_bytes
from .forms import UserResetForgotPasswordForm
from .tokens import password_reset_token
User = get_user_model()


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

        self.ally = Ally.objects.create(user=self.user,
                                        user_type=['Graduate Student'],
                                        hawk_id=self.user.username,
                                        area_of_research=['Computer Science and Engineering'],
                                        interested_in_mentoring=True,
                                        willing_to_offer_lab_shadowing=True,
                                        interested_in_connecting_with_other_mentors=True,
                                        willing_to_volunteer_for_events=True,
                                        interested_in_mentor_training=True)

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
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = True
        self.ally.save()
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
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = True
        self.ally.save()
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.OK)

    def test_if_confirmation_link_expired(self):
        """
        The unique link to reset password does not work
        """
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = False
        self.ally.save()
        token = password_reset_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        link = reverse('sap:password-forgot-confirm', args=[uid, token])

        request = self.client.get(link)
        self.assertEqual(request.status_code, HTTPStatus.FOUND)

    def test_reset_password_success(self):
        """
        Successfully create new password.
        """
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = True
        self.ally.save()
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

    def test_reset_password_failure_exprired_link(self):
        """
        Fail to create new password due to expired link.
        """
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = True
        self.ally.save()
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

        self.ally.reset_password = False
        self.ally.save()

        response = self.client.post(
            link, data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, "Password reset link is expired. Please request a new password reset.")

    def test_reset_password_mismatched(self):
        """
        Fail to create new password.
        """
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = True
        self.ally.save()
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
        self.user.is_active = True
        self.user.save()
        self.ally.reset_password = True
        self.ally.save()
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


# class ForgotPasswordDoneView(TestCase):
#     """
#     Unit tests for ForgotPasswordDoneView
#     """
#
#     def setUp(self):
#         self.username = 'admin'
#         self.username_active = 'user_active'
#         self.password = 'admin_password1'
#         self.email = 'email@test.com'
#         self.email_active = 'email_active@test.com'
#         self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
#         self.user_active = User.objects.create_user(username=self.username_active, email=self.email_active,
#                                                     password=self.password,
#                                                     is_active=True)
#         self.client = Client()
#
#     def test_forgotpassword_if_keyerror(self):
#         """
#         If keyerror
#         """
#         self.client.logout()
#         response = self.client.get(reverse('sap:password-forgot-done'))
#         self.assertEqual(response.status_code, 302)
#
#     def test_forgotpassword_if_keyerror_and_is_authenticated(self):
#         """
#         If keyerror and is_authenticated
#         """
#         self.client.login(username=self.username, password=self.password)
#         response = self.client.get(reverse('sap:password-forgot-done'))
#         self.assertEqual(response.status_code, 302)


class FeedbackTest(TestCase):
    """
    Unit tests for forgot password feature
    """

    def setUp(self):
        self.username = 'user1'
        self.password = 'user_password1'
        self.email = 'email1@test.com'
        self.client = Client()
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            is_active=True,
        )

        self.ally = Ally.objects.create(
            user=self.user,
            user_type=['Graduate Student'],
            hawk_id=self.user.username,
            area_of_research=['Computer Science and Engineering'],
            interested_in_mentoring=True,
            willing_to_offer_lab_shadowing=True,
            interested_in_connecting_with_other_mentors=True,
            willing_to_volunteer_for_events=True,
            interested_in_mentor_training=True,
        )

    def test_get(self):
        """
        Successfully get the feedback page
        """
        self.client.login(username=self.username, password=self.password)
        link = reverse('sap:feedback')
        response = self.client.get(link)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_fail(self):
        """
        Fail to get the feedback page
        """
        self.client.login(username=self.username, password=self.password)
        self.client.logout()
        link = reverse('sap:feedback')
        response = self.client.get(link)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post(self):
        """
        Successfully send the feedback
        """
        self.client.login(username=self.username, password=self.password)
        link = reverse('sap:feedback')

        data = {
            "email_address": "test@uiowa.edu",
            "message": "good app!"
        }

        response = self.client.post(
            link, data=data, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
