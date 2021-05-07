"""
contains unit tests for sap app
"""
from http import HTTPStatus
from notifications.models import Notification

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client  # tests file
from django.urls import reverse
from sap.models import Ally
from sap.views_v2 import urlsafe_base64_encode, force_bytes
from sap.models import AllyMenteeRelation, AllyMentorRelation

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


def check_non_existant(mentor_id, mentee_id):
    """
    checks if mentor relation was deleted
    """
    try:
        AllyMenteeRelation.objects.get(ally_id=mentor_id)
        AllyMentorRelation.objects.get(ally_id=mentee_id)
        return False
    except ObjectDoesNotExist:
        return True

class MentorshipTests(TestCase):
    """
    Test ally/admin mentorship feature
    """
    def check_supposed_relation(self, mentor_id, mentee_id):
        """
        checks if proper mentor relation exists
        """
        mentor_mentee = AllyMenteeRelation.objects.get(ally_id=mentor_id)
        mentee_mentor = AllyMentorRelation.objects.get(ally_id=mentee_id)

        self.assertEqual(mentee_mentor.mentor_id, mentor_mentee.ally_id)
        self.assertEqual(mentor_mentee.mentee_id, mentee_mentor.ally_id)

    def setUp(self):
        self.mentor_user = User.objects.create_user(username='mentorGuy', password='password123')
        self.mentor_ally = Ally.objects.create(hawk_id=self.mentor_user.username, user=self.mentor_user)
        self.mentor_user2 = User.objects.create_user(username='mentorGuy2', password='password123')
        self.mentor_ally2 = Ally.objects.create(hawk_id=self.mentor_user2.username, user=self.mentor_user2)
        self.mentee_user = User.objects.create_user(username='menteeGuy', password='password123')
        self.mentee_ally = Ally.objects.create(hawk_id=self.mentee_user.username, user=self.mentee_user)
        self.mentee_user2 = User.objects.create_user(username='menteeGuy2', password='password123')
        self.mentee_ally2 = Ally.objects.create(hawk_id=self.mentee_user2.username, user=self.mentee_user2)
        self.admin_user = User.objects.create_user(username='adminGuy', password='password123', is_staff=True)
        self.mentee_mentor = AllyMentorRelation.objects.create(ally_id=self.mentee_ally2.id, mentor_id=self.mentor_ally2.id)
        self.mentor_mentee = AllyMenteeRelation.objects.create(ally_id=self.mentor_ally2.id, mentee_id=self.mentee_ally2.id)
        self.client = Client()

    def test_send_non_existing_mentor_invitation(self):
        """
        test ability for mentees to ask to be mentored
        """
        response = self.client.get(reverse('sap:notify_mentor', args=["junkNotArealUser1000"]))
        self.assertEqual(302, response.status_code)

    def test_send_non_existing_mentee_inviation(self):
        """
        test ability for mentors to ask to mentor a mentee
        """
        response = self.client.get(reverse('sap:notify_mentee', args=["junkNotArealUser100000"]))
        self.assertEqual(response.status_code, 302)

    def test_add_and_delete_as_mentee(self):
        """
        test adding/deleting a mentor via notification
        """
        self.client.login(username=self.mentor_user.username, password='password123')
        self.client.get(reverse('sap:notify_mentee', args=[self.mentee_user.username]))
        notification = list(Notification.objects.all())
        notification = notification[-1]
        self.client.logout()

        self.client.login(username=self.mentee_user.username, password='password123')
        response = self.client.get(reverse('sap:add_mentor',
                                           args=[notification.action_object.user.username, notification.id]), follow=True)
        notification = list(Notification.objects.all())
        notification = notification[-1]
        self.assertEqual(notification.action_object, self.mentee_ally)
        self.assertEqual(200, response.status_code)
        self.check_supposed_relation(self.mentor_ally.id, self.mentee_ally.id)
        self.client.get(reverse('sap:add_mentor', args=['junkNotARealUser', notification.id]))
        self.client.logout()

        self.client.login(username=self.mentor_user.username, password='password123')
        self.client.get(reverse('sap:delete_mentee', args=[notification.action_object.user.username, 'notification']))
        self.assertTrue(check_non_existant(self.mentor_ally.id, self.mentee_ally.id))
        self.client.get(reverse('sap:delete_mentee', args=[notification.action_object.user.username, 'notification']))

    def test_add_and_delete_as_mentor(self):
        """
        test adding/deleting a mentee via notification
        """
        self.client.login(username=self.mentee_user.username, password='password123')
        response = self.client.get(reverse('sap:notify_mentor', args=[self.mentor_user.username]))
        self.assertEqual(302, response.status_code)
        notification = list(Notification.objects.all())
        notification = notification[-1]
        self.assertEqual(notification.action_object, self.mentee_ally)
        self.client.logout()

        self.client.login(username=self.mentor_user.username, password='password123')
        response = self.client.get(reverse('sap:add_mentee', args=[notification.action_object.user.username,
                                                                   notification.id]))
        self.assertEqual(response.status_code, 302)
        notification = list(Notification.objects.all())
        notification = notification[-1]
        self.assertEqual(notification.action_object, self.mentor_ally)
        self.client.get(reverse('sap:add_mentee', args=['junkNotARealUser', notification.id]))
        self.client.logout()

        self.client.login(username=self.mentee_user.username, password='password123')
        self.client.get(reverse('sap:delete_mentor', args=[notification.action_object.user.username, 'notification']))
        self.assertTrue(check_non_existant(self.mentor_ally.id, self.mentee_ally.id))
        self.client.get(reverse('sap:delete_mentor', args=[notification.action_object.user.username, 'notification']))

    def test_delete_mentor_admin(self):
        """
        Test delete mentor mentee pair as an admin
        """
        self.client.login(username='adminGuy', password='password123')
        self.client.get(reverse('sap:admin_delete_mentor_mentee', args=[self.mentee_user2.username,
                                                                                   self.mentor_user2.username,
                                                                                   'mentee']))
        self.assertTrue(check_non_existant(self.mentor_ally2.id, self.mentee_ally2.id))

    def test_add_mentor_admin(self):
        """
        Test add mentor to mentee as admin
        """
        self.client.login(username='adminGuy', password='password123')
        response = self.client.get(reverse('sap:admin_add_mentor_mentee', args=[self.mentor_user2.username,
                                                                                self.mentee_user2.username]))
        self.assertEqual(response.status_code, 200)
        self.client.get(reverse('sap:admin_add_mentor_mentee', args=[self.mentor_user2.username,
                                                                                self.mentee_user2.username]))
        self.check_supposed_relation(self.mentor_ally2.id, self.mentee_ally2.id)

    def test_get(self):
        """
        Test if page can render to add mentor/mentee as an admin
        """
        self.client.login(username='adminGuy', password='password123')
        response = self.client.get(reverse('sap:admin_add_mentor_mentee', args=[self.mentor_ally2, 'addMentee']))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('sap:admin_add_mentor_mentee', args=[self.mentee_ally2, 'addMentor']))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        """
        Test if you mentees may be added via post request
        """
        self.client.login(username='adminGuy', password='password123')
        self.client.post(reverse('sap:admin_add_mentor_mentee', args=[self.mentor_ally, 'addMentee']),
                                    {
                                        'csrfmiddlewaretoken': [
                                            'AAIHnJBSnR9fQdHP6yTjGRPQSE8HmiRI7oc3tPv0RyJrMoAyXpq93geUfDTH6QCk'],
                                        'mentees-to-add': [self.mentee_user.username]
                                    })
        self.check_supposed_relation(self.mentor_ally.id, self.mentee_ally.id)


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
