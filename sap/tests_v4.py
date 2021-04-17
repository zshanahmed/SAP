"""
contains unit tests for sap app
"""
import os
import time
from django.contrib.auth import get_user_model
from django.test import TestCase, Client  # tests file
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
        curr_timestamp = str(time.time()).split('.')[0]
        local_file_name = "quickstart" + curr_timestamp + ".txt"
        upload_file_path = os.path.join(local_path, local_file_name)

        # Write text to the file
        file = open(upload_file_path, 'w')
        file.write("Hello, World!")
        file.close()

        uploaded_resource_url_in_cloud = upload_file_to_azure(local_file_name, called_by_test_function=True)
        expected_resource_url_in_cloud = "https://sepibafiles.blob.core.windows.net/sepibacontainer/" + local_file_name

        self.assertEqual(uploaded_resource_url_in_cloud, expected_resource_url_in_cloud)
