"""
contains unit tests for sap app
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file

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
