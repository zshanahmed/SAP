"""
contains unit tests for sap app
"""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file

from sap.models import EventInviteeRelation, AllyStudentCategoryRelation, StudentCategories, Ally, Event

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
